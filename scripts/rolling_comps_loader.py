"""
Rolling Comparable Sales Loader for NYC Real Estate AI

Fetches comparable sales from NYC DOF Rolling Sales and ACRIS,
calculates YoY changes, and populates ComparableSales table.

Data Sources:
- DOF Rolling Sales: https://www.nyc.gov/site/finance/taxes/property-rolling-sales-data.page
- ACRIS: Historical sales for YoY baseline

Requirements:
    pip install pandas openpyxl pyairtable sodapy python-dotenv requests
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import requests
from sodapy import Socrata
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
NYC_OPEN_DATA_APP_TOKEN = os.getenv("NYC_OPEN_DATA_APP_TOKEN")

# Initialize Airtable
airtable = Api(AIRTABLE_API_KEY)
properties_table = airtable.table(AIRTABLE_BASE_ID, 'Properties')
comps_table = airtable.table(AIRTABLE_BASE_ID, 'ComparableSales')
neighborhoods_table = airtable.table(AIRTABLE_BASE_ID, 'Neighborhoods')


class DOFRollingSalesFetcher:
    """Fetch NYC Department of Finance Rolling Sales data."""

    # DOF Rolling Sales URLs by borough (Excel files)
    ROLLING_SALES_URLS = {
        "Manhattan": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xlsx",
        "Bronx": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xlsx",
        "Brooklyn": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xlsx",
        "Queens": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xlsx",
        "Staten Island": "https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xlsx"
    }

    def __init__(self):
        self.session = requests.Session()

    def fetch_rolling_sales(self, borough: str) -> pd.DataFrame:
        """
        Download and parse DOF Rolling Sales Excel file for a borough.

        Args:
            borough: Borough name (Manhattan, Brooklyn, etc.)

        Returns:
            DataFrame of sales records
        """
        url = self.ROLLING_SALES_URLS.get(borough)
        if not url:
            print(f"Invalid borough: {borough}")
            return pd.DataFrame()

        print(f"Downloading Rolling Sales for {borough}...")

        try:
            # Download Excel file
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Read Excel (usually has a header row to skip)
            df = pd.read_excel(
                response.content,
                skiprows=4,  # DOF files have 4 header rows
                engine='openpyxl'
            )

            # Standardize column names (DOF uses uppercase with spaces)
            df.columns = df.columns.str.strip().str.upper()

            print(f"  Loaded {len(df)} sales records")

            return df

        except Exception as e:
            print(f"Error downloading Rolling Sales: {e}")
            return pd.DataFrame()

    def filter_condo_sales(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for valid condo sales only.

        Args:
            df: Raw DOF sales data

        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df

        # DOF Building Class Code for condos: R* (residential condos)
        # Common codes: R4 (elevator condos), R2 (walk-up condos)
        df_condos = df[df['BUILDING CLASS CATEGORY'].str.contains('CONDO', case=False, na=False)]

        # Filter out non-arms-length sales
        # Sale price should be reasonable
        df_condos = df_condos[
            (df_condos['SALE PRICE'] >= 100000) &
            (df_condos['SALE PRICE'] <= 50000000)
        ]

        # Remove rows with missing critical data
        df_condos = df_condos.dropna(subset=['SALE PRICE', 'SALE DATE', 'ADDRESS'])

        print(f"  Filtered to {len(df_condos)} valid condo sales")

        return df_condos

    def parse_sale_record(self, row: pd.Series, borough: str) -> Dict:
        """
        Parse a DOF sale record into standard format.

        Args:
            row: DataFrame row
            borough: Borough name

        Returns:
            Dictionary with standardized fields
        """
        # Extract unit number from address if present
        address = str(row.get('ADDRESS', '')).strip()
        unit_number = self._extract_unit_number(address)

        # Parse SQFT (may be in GROSS SQUARE FEET or LAND SQUARE FEET)
        sqft_columns = ['GROSS SQUARE FEET', 'RESIDENTIAL UNITS', 'LAND SQUARE FEET']
        sqft = 0
        for col in sqft_columns:
            if col in row and pd.notna(row[col]) and float(row[col]) > 0:
                sqft = int(float(row[col]))
                break

        return {
            "BBL": str(row.get('BBL', '')).strip(),
            "Address": address,
            "BuildingName": None,  # Not in DOF data
            "UnitNumber": unit_number,
            "Bedrooms": None,  # Not in DOF data
            "Bathrooms": None,  # Not in DOF data
            "SQFT": sqft if sqft > 0 else None,
            "SaleDate": pd.to_datetime(row['SALE DATE']).strftime("%Y-%m-%d") if pd.notna(row.get('SALE DATE')) else None,
            "SalePrice": int(float(row['SALE PRICE'])) if pd.notna(row.get('SALE PRICE')) else 0,
            "Borough": borough,
            "ZipCode": str(row.get('ZIP CODE', '')).strip()[:5] if pd.notna(row.get('ZIP CODE')) else None,
            "DocumentID": None,  # Would need ACRIS lookup
            "SaleType": "Arms Length",  # Assume valid since filtered
            "DataSource": "DOF Rolling Sales",
            "CompQuality": None,  # Determined later when matching to properties
            "PriorYearSalePrice": None  # Calculated separately
        }

    def _extract_unit_number(self, address: str) -> Optional[str]:
        """Extract unit/apartment number from address string."""
        # Common patterns: "123 MAIN ST, APT 5B", "123 MAIN ST #5B", "123 MAIN ST 5B"
        import re

        patterns = [
            r'(?:APT|UNIT|#)\s*([A-Z0-9]+)',
            r',\s*([A-Z0-9]+)$',  # Trailing unit after comma
        ]

        for pattern in patterns:
            match = re.search(pattern, address.upper())
            if match:
                return match.group(1)

        return None


class ACRISYoYCalculator:
    """Calculate year-over-year changes using ACRIS historical data."""

    def __init__(self):
        self.client = Socrata(
            "data.cityofnewyork.us",
            NYC_OPEN_DATA_APP_TOKEN,
            timeout=30
        )
        self.sales_dataset = "bnx9-e6tj"

    def find_prior_year_sale(self, bbl: str, sale_date: str, sqft: int) -> Optional[Dict]:
        """
        Find a comparable sale from 12-18 months prior to establish YoY baseline.

        Args:
            bbl: 10-digit BBL identifier
            sale_date: Sale date (YYYY-MM-DD)
            sqft: Square footage for matching

        Returns:
            Prior year sale record or None
        """
        sale_dt = datetime.strptime(sale_date, "%Y-%m-%d")
        start_date = (sale_dt - timedelta(days=540)).strftime("%Y-%m-%d")  # 18 months before
        end_date = (sale_dt - timedelta(days=330)).strftime("%Y-%m-%d")    # 11 months before

        try:
            # Query ACRIS for sales at same BBL in prior year window
            # Note: ACRIS doesn't have BBL in main sales table, need to join
            # For simplicity, we'll use address matching (in production, use BBL join)

            # This is a simplified approach - full implementation would join ACRIS tables
            print(f"  Searching for prior year comp: BBL {bbl}, window {start_date} to {end_date}")

            # Placeholder: In production, this would query ACRIS properly
            # For now, return None and we'll calculate YoY at building level
            return None

        except Exception as e:
            print(f"  Error querying ACRIS: {e}")
            return None

    def calculate_building_yoy(self, bbl_prefix: str, current_date: str,
                               current_ppsf: float) -> Optional[float]:
        """
        Calculate YoY change using building-level median from prior year.

        Args:
            bbl_prefix: First 7 digits of BBL (borough-block-lot without unit)
            current_date: Current sale date
            current_ppsf: Current PPSF

        Returns:
            YoY percentage change or None
        """
        # In production, would query all sales in same building from prior year
        # and calculate median PPSF, then compare to current

        # Placeholder implementation
        return None


class CompsMatchingEngine:
    """Match properties to their comparable sales."""

    def __init__(self, airtable_api):
        self.airtable = airtable_api
        self.properties = None
        self.comps = None

    def load_data(self):
        """Load properties and comps from Airtable."""
        print("Loading properties and comps from Airtable...")
        self.properties = properties_table.all()
        self.comps = comps_table.all()
        print(f"  Loaded {len(self.properties)} properties, {len(self.comps)} comps")

    def find_comps_for_property(self, property_record: Dict) -> List[str]:
        """
        Find comp record IDs that match this property.

        Matching criteria (in priority order):
        1. Same building (BBL prefix match)
        2. Same zip code + similar beds/sqft
        3. Same neighborhood

        Args:
            property_record: Airtable property record

        Returns:
            List of comp record IDs to link
        """
        fields = property_record['fields']
        address = fields.get('Address', '')
        beds = fields.get('Bedrooms')
        sqft = fields.get('SQFT')
        neighborhood = fields.get('Neighborhood')

        if not sqft or sqft == 0:
            return []

        matched_comps = []

        # Priority 1: Same building
        building_address = self._extract_building_address(address)

        for comp in self.comps:
            comp_fields = comp['fields']
            comp_address = comp_fields.get('Address', '')
            comp_building = self._extract_building_address(comp_address)

            # Same building check
            if building_address and comp_building and building_address.upper() == comp_building.upper():
                comp_beds = comp_fields.get('Bedrooms')
                comp_sqft = comp_fields.get('SQFT', 0)

                # Beds within ±1, SQFT within ±20%
                beds_match = not beds or not comp_beds or abs(beds - comp_beds) <= 1
                sqft_match = comp_sqft > 0 and abs(sqft - comp_sqft) / sqft <= 0.20

                if beds_match and sqft_match:
                    matched_comps.append(comp['id'])
                    # Update comp quality
                    try:
                        comps_table.update(comp['id'], {"CompQuality": "Excellent"})
                    except:
                        pass

        # If <3 comps from same building, expand to zip code
        if len(matched_comps) < 3:
            zip_code = self._extract_zip(address)

            for comp in self.comps:
                if comp['id'] in matched_comps:
                    continue

                comp_fields = comp['fields']
                comp_zip = comp_fields.get('ZipCode')
                comp_beds = comp_fields.get('Bedrooms')
                comp_sqft = comp_fields.get('SQFT', 0)

                if zip_code and comp_zip == zip_code:
                    beds_match = not beds or not comp_beds or beds == comp_beds
                    sqft_match = comp_sqft > 0 and abs(sqft - comp_sqft) / sqft <= 0.15

                    if beds_match and sqft_match:
                        matched_comps.append(comp['id'])
                        try:
                            comps_table.update(comp['id'], {"CompQuality": "Good"})
                        except:
                            pass

        # Limit to top 10 most recent comps
        return matched_comps[:10]

    def link_all_properties(self):
        """Link all properties to their comps."""
        print("\nLinking properties to comparable sales...")

        linked_count = 0
        for i, prop in enumerate(self.properties, 1):
            prop_id = prop['id']
            address = prop['fields'].get('Address', '')

            print(f"[{i}/{len(self.properties)}] {address}")

            comp_ids = self.find_comps_for_property(prop)

            if comp_ids:
                try:
                    properties_table.update(prop_id, {
                        "ComparableSales": comp_ids
                    })
                    print(f"  ✓ Linked {len(comp_ids)} comps")
                    linked_count += 1
                except Exception as e:
                    print(f"  ✗ Error linking: {e}")
            else:
                print(f"  - No comps found")

        print(f"\n✓ Linked {linked_count}/{len(self.properties)} properties to comps")

    def _extract_building_address(self, address: str) -> str:
        """Extract building address without unit number."""
        # Remove unit patterns
        import re
        patterns = [
            r',?\s*(?:APT|UNIT|#)\s*[A-Z0-9]+',
            r',\s*[A-Z0-9]+$'
        ]

        clean = address.upper()
        for pattern in patterns:
            clean = re.sub(pattern, '', clean)

        return clean.strip()

    def _extract_zip(self, address: str) -> Optional[str]:
        """Extract zip code from address."""
        import re
        match = re.search(r'\b(\d{5})\b', address)
        return match.group(1) if match else None


class RollingCompsLoader:
    """Main orchestrator for loading comparable sales."""

    def __init__(self):
        self.dof = DOFRollingSalesFetcher()
        self.acris = ACRISYoYCalculator()
        self.matcher = CompsMatchingEngine(airtable)

    def load_comps_for_borough(self, borough: str, months_back: int = 24):
        """
        Load comparable sales for a borough.

        Args:
            borough: Borough name
            months_back: How many months of sales to load
        """
        print(f"\n{'='*60}")
        print(f"Loading Comparable Sales: {borough}")
        print(f"{'='*60}\n")

        # 1. Fetch DOF Rolling Sales
        df = self.dof.fetch_rolling_sales(borough)

        if df.empty:
            print("No data fetched. Exiting.")
            return

        # 2. Filter for valid condo sales
        df_condos = self.dof.filter_condo_sales(df)

        # 3. Filter by date (last N months)
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        df_condos['SALE DATE'] = pd.to_datetime(df_condos['SALE DATE'])
        df_recent = df_condos[df_condos['SALE DATE'] >= cutoff_date]

        print(f"\nFiltered to {len(df_recent)} sales from last {months_back} months")

        # 4. Parse and add to Airtable
        added_count = 0
        skipped_count = 0

        for idx, row in df_recent.iterrows():
            comp_data = self.dof.parse_sale_record(row, borough)

            # Skip if missing critical data
            if not comp_data['SalePrice'] or not comp_data['SaleDate']:
                skipped_count += 1
                continue

            # Check if already exists (by BBL + sale date)
            bbl = comp_data['BBL']
            sale_date = comp_data['SaleDate']

            existing = comps_table.all(
                formula=f"AND({{BBL}}='{bbl}', {{SaleDate}}='{sale_date}')"
            )

            if existing:
                skipped_count += 1
                continue

            # Add to Airtable
            try:
                # Remove None values
                comp_data_clean = {k: v for k, v in comp_data.items() if v is not None}

                comps_table.create(comp_data_clean)
                added_count += 1

                if added_count % 10 == 0:
                    print(f"  Progress: {added_count} comps added...")

            except Exception as e:
                print(f"  Error adding comp: {e}")
                skipped_count += 1

        print(f"\n{'='*60}")
        print(f"Results: {added_count} added, {skipped_count} skipped")
        print(f"{'='*60}")

    def load_all_boroughs(self, months_back: int = 24):
        """Load comps for all NYC boroughs."""
        boroughs = ["Manhattan", "Brooklyn", "Queens"]  # Start with main 3

        for borough in boroughs:
            self.load_comps_for_borough(borough, months_back)

    def calculate_yoy_for_all_comps(self):
        """
        Calculate YoY changes for all comps that don't have it yet.

        This is a placeholder - full implementation would:
        1. For each comp, find prior year sale at same address/building
        2. Calculate YoY change
        3. Update PriorYearSalePrice and let formulas calculate YoY
        """
        print("\nCalculating YoY changes...")
        print("Note: Full YoY calculation requires ACRIS integration")
        print("For now, comps will aggregate from building-level trends")

    def link_properties_to_comps(self):
        """Link all properties to their comparable sales."""
        self.matcher.load_data()
        self.matcher.link_all_properties()


def main():
    """Main execution."""
    import sys

    if len(sys.argv) < 2:
        print("NYC Real Estate AI - Rolling Comps Loader")
        print("\nUsage:")
        print("  Load one borough:       python rolling_comps_loader.py --borough Manhattan")
        print("  Load all boroughs:      python rolling_comps_loader.py --all")
        print("  Link properties:        python rolling_comps_loader.py --link")
        print("  Calculate YoY:          python rolling_comps_loader.py --yoy")
        print("  Full pipeline:          python rolling_comps_loader.py --full")
        return

    loader = RollingCompsLoader()

    if sys.argv[1] == '--borough':
        if len(sys.argv) < 3:
            print("Error: Specify borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)")
            return
        borough = sys.argv[2]
        months = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        loader.load_comps_for_borough(borough, months)

    elif sys.argv[1] == '--all':
        months = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        loader.load_all_boroughs(months)

    elif sys.argv[1] == '--link':
        loader.link_properties_to_comps()

    elif sys.argv[1] == '--yoy':
        loader.calculate_yoy_for_all_comps()

    elif sys.argv[1] == '--full':
        print("Running full pipeline...\n")
        months = int(sys.argv[2]) if len(sys.argv) > 2 else 24

        # Step 1: Load comps
        loader.load_all_boroughs(months)

        # Step 2: Calculate YoY
        loader.calculate_yoy_for_all_comps()

        # Step 3: Link to properties
        loader.link_properties_to_comps()

        print("\n✓ Full pipeline complete!")


if __name__ == "__main__":
    main()
