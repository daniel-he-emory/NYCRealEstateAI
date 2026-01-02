"""
Historical Data Loader for NYC Real Estate AI

Fetches historical sales data from NYC ACRIS and property data from PLUTO
to populate historical trends and valuation metrics.

Data Sources:
- ACRIS: NYC deed sales records (1966-present)
- PLUTO: Primary Land Use Tax Lot Output (annual release)
- DOF Annualized Sales: Quarterly median sales data

Requirements:
    pip install sodapy pandas pyairtable python-dotenv requests
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from sodapy import Socrata
from pyairtable import Api
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
NYC_OPEN_DATA_APP_TOKEN = os.getenv("NYC_OPEN_DATA_APP_TOKEN")  # Optional but recommended

# Initialize Airtable
airtable = Api(AIRTABLE_API_KEY)
properties_table = airtable.table(AIRTABLE_BASE_ID, 'Properties')
historical_sales_table = airtable.table(AIRTABLE_BASE_ID, 'HistoricalSales')
neighborhoods_table = airtable.table(AIRTABLE_BASE_ID, 'Neighborhoods')
market_metrics_table = airtable.table(AIRTABLE_BASE_ID, 'MarketMetrics')


class ACRISDataFetcher:
    """Fetch NYC deed sales records from ACRIS via Socrata API."""

    def __init__(self):
        self.client = Socrata(
            "data.cityofnewyork.us",
            NYC_OPEN_DATA_APP_TOKEN,
            timeout=30
        )
        self.sales_dataset = "bnx9-e6tj"  # ACRIS Real Property Master dataset

    def fetch_sales_by_address(self, address: str, borough: str, years_back: int = 10) -> List[Dict]:
        """
        Fetch historical sales for a specific address.

        Args:
            address: Street address (e.g., "4610 CENTER BLVD")
            borough: NYC borough (Manhattan, Brooklyn, Queens, Bronx, Staten Island)
            years_back: How many years of history to fetch

        Returns:
            List of sale records
        """
        # Convert borough to ACRIS code
        borough_codes = {
            "Manhattan": "1",
            "Bronx": "2",
            "Brooklyn": "3",
            "Queens": "4",
            "Staten Island": "5"
        }
        borough_code = borough_codes.get(borough)

        if not borough_code:
            print(f"Invalid borough: {borough}")
            return []

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years_back * 365)

        # Format address for query
        address_clean = address.upper().strip()

        try:
            # Query ACRIS dataset
            results = self.client.get(
                self.sales_dataset,
                where=f"borough = '{borough_code}' AND address LIKE '%{address_clean}%'",
                order="document_date DESC",
                limit=50
            )

            print(f"Found {len(results)} sales records for {address}, {borough}")
            return results

        except Exception as e:
            print(f"Error fetching ACRIS data: {e}")
            return []

    def fetch_neighborhood_sales(self, neighborhood: str, borough: str,
                                 start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch all condo sales in a neighborhood for trend analysis.

        Args:
            neighborhood: Neighborhood name
            borough: Borough name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame of sales records
        """
        borough_codes = {
            "Manhattan": "1",
            "Bronx": "2",
            "Brooklyn": "3",
            "Queens": "4",
            "Staten Island": "5"
        }
        borough_code = borough_codes.get(borough)

        try:
            # Query for all sales in date range
            # Note: ACRIS doesn't have neighborhood field, would need to join with PLUTO
            results = self.client.get(
                self.sales_dataset,
                where=f"borough = '{borough_code}' AND document_date BETWEEN '{start_date}' AND '{end_date}'",
                order="document_date DESC",
                limit=5000
            )

            df = pd.DataFrame.from_records(results)
            return df

        except Exception as e:
            print(f"Error fetching neighborhood sales: {e}")
            return pd.DataFrame()

    def parse_sale_record(self, record: Dict) -> Dict:
        """Parse ACRIS record into clean format."""
        return {
            "DocumentID": record.get("document_id"),
            "RecordedDate": record.get("document_date"),
            "Address": record.get("address"),
            "Borough": self._borough_code_to_name(record.get("borough")),
            "SalePrice": float(record.get("sale_price", 0)) if record.get("sale_price") else 0,
            "PropertyType": "Condo"  # Would need additional data to determine
        }

    def _borough_code_to_name(self, code: str) -> str:
        """Convert borough code to name."""
        codes = {
            "1": "Manhattan",
            "2": "Bronx",
            "3": "Brooklyn",
            "4": "Queens",
            "5": "Staten Island"
        }
        return codes.get(code, "Unknown")


class PLUTODataFetcher:
    """Fetch NYC property data from PLUTO dataset."""

    def __init__(self):
        # PLUTO is downloaded as bulk CSV/Shapefile, not API
        self.pluto_url = "https://data.cityofnewyork.us/resource/64uk-42ks.json"
        self.client = Socrata(
            "data.cityofnewyork.us",
            NYC_OPEN_DATA_APP_TOKEN,
            timeout=30
        )

    def fetch_property_by_address(self, address: str, borough: str) -> Optional[Dict]:
        """
        Fetch PLUTO data for a specific property.

        Args:
            address: Street address
            borough: Borough name

        Returns:
            Property data including assessed value, sq ft, year built
        """
        try:
            # Clean address for matching
            address_parts = address.split()
            house_number = address_parts[0] if address_parts else ""
            street_name = " ".join(address_parts[1:]) if len(address_parts) > 1 else ""

            results = self.client.get(
                "64uk-42ks",  # PLUTO dataset ID
                where=f"address LIKE '%{street_name.upper()}%' AND borough = '{borough.upper()}'",
                limit=10
            )

            if results:
                # Return first match
                prop = results[0]
                return {
                    "AssessedValue": float(prop.get("assesstot", 0)),
                    "LotArea": float(prop.get("lotarea", 0)),
                    "BuildingArea": float(prop.get("bldgarea", 0)),
                    "YearBuilt": int(prop.get("yearbuilt", 0)) if prop.get("yearbuilt") else None,
                    "NumFloors": int(prop.get("numfloors", 0)) if prop.get("numfloors") else None,
                    "ZoningDistrict": prop.get("zonedist1"),
                    "LandUse": prop.get("landuse")
                }

            return None

        except Exception as e:
            print(f"Error fetching PLUTO data: {e}")
            return None


class HistoricalTrendCalculator:
    """Calculate historical price trends for properties."""

    def __init__(self, airtable_api):
        self.airtable = airtable_api

    def calculate_ppsf_trends(self, property_address: str, neighborhood: str) -> Dict:
        """
        Calculate historical PPSF averages for a property.

        Args:
            property_address: Property address
            neighborhood: Neighborhood name

        Returns:
            Dictionary with 1yr, 3yr, 5yr PPSF averages
        """
        # Fetch historical sales from HistoricalSales table
        sales = historical_sales_table.all(
            formula=f"{{Neighborhood}}='{neighborhood}'"
        )

        if not sales:
            return {
                "HistoricalPPSF_1YrAvg": None,
                "HistoricalPPSF_3YrAvg": None,
                "HistoricalPPSF_5YrAvg": None
            }

        # Convert to DataFrame for analysis
        df = pd.DataFrame([{
            "RecordedDate": s['fields'].get('RecordedDate'),
            "PricePerSQFT": s['fields'].get('PricePerSQFT', 0)
        } for s in sales])

        df['RecordedDate'] = pd.to_datetime(df['RecordedDate'])
        df = df[df['PricePerSQFT'] > 0]

        now = datetime.now()

        # Calculate averages
        one_year_ago = now - timedelta(days=365)
        three_years_ago = now - timedelta(days=365 * 3)
        five_years_ago = now - timedelta(days=365 * 5)

        ppsf_1yr = df[df['RecordedDate'] >= one_year_ago]['PricePerSQFT'].mean()
        ppsf_3yr = df[df['RecordedDate'] >= three_years_ago]['PricePerSQFT'].mean()
        ppsf_5yr = df[df['RecordedDate'] >= five_years_ago]['PricePerSQFT'].mean()

        return {
            "HistoricalPPSF_1YrAvg": round(ppsf_1yr, 2) if not pd.isna(ppsf_1yr) else None,
            "HistoricalPPSF_3YrAvg": round(ppsf_3yr, 2) if not pd.isna(ppsf_3yr) else None,
            "HistoricalPPSF_5YrAvg": round(ppsf_5yr, 2) if not pd.isna(ppsf_5yr) else None
        }


class DataLoader:
    """Main class to orchestrate historical data loading."""

    def __init__(self):
        self.acris = ACRISDataFetcher()
        self.pluto = PLUTODataFetcher()
        self.trends = HistoricalTrendCalculator(airtable)

    def load_property_historical_data(self, property_record: Dict) -> bool:
        """
        Load all historical data for a single property.

        Args:
            property_record: Airtable property record

        Returns:
            True if successful
        """
        fields = property_record['fields']
        address = fields.get('Address')
        neighborhood_link = fields.get('Neighborhood')

        if not address:
            print(f"Skipping property without address: {property_record['id']}")
            return False

        # Parse address to get borough
        # Simplified - in production, use geocoding or address parsing
        borough = self._extract_borough_from_address(address)

        print(f"\nProcessing: {address}")

        # 1. Fetch ACRIS sales history
        sales = self.acris.fetch_sales_by_address(address, borough, years_back=10)

        # Add sales to HistoricalSales table
        for sale in sales:
            parsed_sale = self.acris.parse_sale_record(sale)
            if parsed_sale['SalePrice'] > 0:  # Filter out non-arms-length sales
                try:
                    # Check if already exists
                    existing = historical_sales_table.all(
                        formula=f"{{DocumentID}}='{parsed_sale['DocumentID']}'"
                    )
                    if not existing:
                        historical_sales_table.create(parsed_sale)
                        print(f"  Added sale: {parsed_sale['RecordedDate']} - ${parsed_sale['SalePrice']:,.0f}")
                except Exception as e:
                    print(f"  Error adding sale: {e}")

        # 2. Fetch PLUTO data
        pluto_data = self.pluto.fetch_property_by_address(address, borough)

        # 3. Calculate historical trends
        if neighborhood_link:
            neighborhood_name = self._get_neighborhood_name(neighborhood_link[0])
            trends = self.trends.calculate_ppsf_trends(address, neighborhood_name)
        else:
            trends = {}

        # 4. Update property record with new data
        update_fields = {}

        if pluto_data:
            if pluto_data.get('AssessedValue'):
                update_fields['AssessedValue'] = pluto_data['AssessedValue']
            if pluto_data.get('YearBuilt') and not fields.get('YearBuilt'):
                update_fields['YearBuilt'] = pluto_data['YearBuilt']

        # Add historical PPSF data
        update_fields.update(trends)

        if update_fields:
            try:
                properties_table.update(property_record['id'], update_fields)
                print(f"  ✓ Updated property with {len(update_fields)} fields")
                return True
            except Exception as e:
                print(f"  ✗ Error updating property: {e}")
                return False

        return True

    def load_all_properties(self):
        """Load historical data for all properties in database."""
        print("Fetching all properties...")
        properties = properties_table.all()

        print(f"Found {len(properties)} properties\n")
        print("=" * 60)

        success_count = 0
        for i, prop in enumerate(properties, 1):
            print(f"\n[{i}/{len(properties)}]")
            if self.load_property_historical_data(prop):
                success_count += 1

        print("\n" + "=" * 60)
        print(f"Completed: {success_count}/{len(properties)} properties updated successfully")

    def _extract_borough_from_address(self, address: str) -> str:
        """Extract borough from address string."""
        address_lower = address.lower()

        if "manhattan" in address_lower or ", ny 10" in address_lower:
            return "Manhattan"
        elif "brooklyn" in address_lower or ", ny 112" in address_lower:
            return "Brooklyn"
        elif "queens" in address_lower or ", ny 11" in address_lower:
            return "Queens"
        elif "bronx" in address_lower or ", ny 104" in address_lower:
            return "Bronx"
        elif "staten island" in address_lower or ", ny 103" in address_lower:
            return "Staten Island"

        return "Manhattan"  # Default

    def _get_neighborhood_name(self, neighborhood_record_id: str) -> str:
        """Get neighborhood name from record ID."""
        try:
            record = neighborhoods_table.get(neighborhood_record_id)
            return record['fields'].get('NeighborhoodName', '')
        except:
            return ''


class NeighborhoodTrendsLoader:
    """Load neighborhood-level historical trends."""

    def __init__(self):
        self.acris = ACRISDataFetcher()

    def update_neighborhood_historical_ppsf(self, neighborhood_name: str, borough: str):
        """
        Calculate and update historical PPSF for a neighborhood.

        Args:
            neighborhood_name: Name of neighborhood
            borough: Borough name
        """
        print(f"\nUpdating {neighborhood_name}, {borough}...")

        # Fetch all sales in neighborhood from HistoricalSales table
        sales = historical_sales_table.all(
            formula=f"AND({{Neighborhood}}='{neighborhood_name}', {{PropertyType}}='Condo')"
        )

        if not sales:
            print(f"  No sales found for {neighborhood_name}")
            return

        # Convert to DataFrame
        df = pd.DataFrame([{
            "RecordedDate": s['fields'].get('RecordedDate'),
            "PricePerSQFT": s['fields'].get('PricePerSQFT', 0)
        } for s in sales])

        df['RecordedDate'] = pd.to_datetime(df['RecordedDate'])
        df = df[df['PricePerSQFT'] > 0]

        now = datetime.now()

        # Calculate historical medians
        one_year_ago = now - timedelta(days=365)
        three_years_ago = now - timedelta(days=365 * 3)
        five_years_ago = now - timedelta(days=365 * 5)

        ppsf_1yr = df[df['RecordedDate'] >= one_year_ago]['PricePerSQFT'].median()
        ppsf_3yr = df[df['RecordedDate'] >= three_years_ago]['PricePerSQFT'].median()
        ppsf_5yr = df[df['RecordedDate'] >= five_years_ago]['PricePerSQFT'].median()

        # Update neighborhood record
        update_data = {
            "PPSF_1YrAgo": round(ppsf_1yr, 2) if not pd.isna(ppsf_1yr) else None,
            "PPSF_3YrAgo": round(ppsf_3yr, 2) if not pd.isna(ppsf_3yr) else None,
            "PPSF_5YrAgo": round(ppsf_5yr, 2) if not pd.isna(ppsf_5yr) else None
        }

        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if update_data:
            try:
                # Find neighborhood record
                records = neighborhoods_table.all(
                    formula=f"{{NeighborhoodName}}='{neighborhood_name}'"
                )
                if records:
                    neighborhoods_table.update(records[0]['id'], update_data)
                    print(f"  ✓ Updated: PPSF 1yr=${update_data.get('PPSF_1YrAgo'):,.0f}, "
                          f"3yr=${update_data.get('PPSF_3YrAgo'):,.0f}, "
                          f"5yr=${update_data.get('PPSF_5YrAgo'):,.0f}")
            except Exception as e:
                print(f"  ✗ Error updating neighborhood: {e}")

    def update_all_neighborhoods(self):
        """Update historical data for all neighborhoods."""
        neighborhoods = neighborhoods_table.all()

        print(f"Updating {len(neighborhoods)} neighborhoods...")

        for nbhd in neighborhoods:
            fields = nbhd['fields']
            name = fields.get('NeighborhoodName')
            borough = fields.get('Borough')

            if name and borough:
                self.update_neighborhood_historical_ppsf(name, borough)


def main():
    """Main execution."""
    import sys

    if len(sys.argv) < 2:
        print("NYC Real Estate AI - Historical Data Loader")
        print("\nUsage:")
        print("  Load all properties:          python historical_data_loader.py --all")
        print("  Load single property:         python historical_data_loader.py --property <record_id>")
        print("  Update neighborhoods:         python historical_data_loader.py --neighborhoods")
        print("  Test with one property:       python historical_data_loader.py --test")
        return

    loader = DataLoader()
    nbhd_loader = NeighborhoodTrendsLoader()

    if sys.argv[1] == '--all':
        print("Loading historical data for ALL properties...")
        print("This may take 10-30 minutes depending on number of properties.\n")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            loader.load_all_properties()

    elif sys.argv[1] == '--property':
        if len(sys.argv) < 3:
            print("Error: Please provide property record ID")
            return
        record_id = sys.argv[2]
        try:
            prop = properties_table.get(record_id)
            loader.load_property_historical_data(prop)
        except Exception as e:
            print(f"Error loading property: {e}")

    elif sys.argv[1] == '--neighborhoods':
        print("Updating neighborhood historical trends...")
        nbhd_loader.update_all_neighborhoods()

    elif sys.argv[1] == '--test':
        # Test with first property
        print("Test mode: Loading first property only...")
        props = properties_table.all(max_records=1)
        if props:
            loader.load_property_historical_data(props[0])
        else:
            print("No properties found in database")


if __name__ == "__main__":
    main()
