"""
NYC Real Estate Property Data Extractor

This script extracts property information from listing URLs (StreetEasy, Zillow, etc.)
and adds them to the Airtable database.

Requirements:
    pip install openai requests beautifulsoup4 pyairtable python-dotenv
"""

import os
import json
import re
from typing import Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import openai
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

openai.api_key = OPENAI_API_KEY
airtable = Api(AIRTABLE_API_KEY)
properties_table = airtable.table(AIRTABLE_BASE_ID, 'Properties')
neighborhoods_table = airtable.table(AIRTABLE_BASE_ID, 'Neighborhoods')


class PropertyExtractor:
    """Extract property data from listing URLs using OpenAI."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_listing_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from listing URL.

        Args:
            url: Property listing URL

        Returns:
            HTML content as string, or None if fetch fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_text_from_html(self, html: str) -> str:
        """
        Extract clean text from HTML for GPT processing.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text content
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()

        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # Limit to first 3000 chars to stay within token limits
        return text[:3000]

    def extract_property_data_with_gpt(self, listing_text: str, url: str) -> Optional[Dict]:
        """
        Use GPT-4 to extract structured property data from listing text.

        Args:
            listing_text: Cleaned text from listing page
            url: Original listing URL

        Returns:
            Dictionary with extracted property data
        """
        system_prompt = """You are a property data extractor. Extract structured information from real estate listings.

Return ONLY valid JSON with these exact fields:
{
  "address": "Full street address",
  "price": number (current price in dollars),
  "bedrooms": number,
  "bathrooms": number (use decimals like 1.5 if needed),
  "sqft": number (square feet),
  "hoa_monthly": number (monthly HOA/maintenance fees),
  "description": "Full property description",
  "has_elevator": boolean,
  "has_doorman": boolean,
  "has_parking": boolean,
  "has_gym": boolean,
  "has_roof_deck": boolean,
  "pet_friendly": boolean,
  "exposure": "North|South|East|West|Corner|Multiple|Unknown",
  "floor_level": "Low (1-5)|Mid (6-15)|High (16-30)|Penthouse (31+)|Unknown",
  "floor_number": number or null,
  "year_built": number or null,
  "subway_distance": number (walking minutes to nearest subway, estimate if not explicit),
  "nearest_subway_lines": "e.g., 7, E, M",
  "estimated_rent": number (estimated monthly rent based on size/location)
}

IMPORTANT:
- Use null for missing values
- All prices/fees in dollars (not abbreviated)
- Be conservative with estimates
- For has_* fields, use true only if explicitly mentioned
"""

        user_prompt = f"""Extract property data from this listing:

URL: {url}

Listing Content:
{listing_text}

Return property data as JSON:"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            extracted_data = json.loads(response.choices[0].message.content)
            extracted_data["listing_url"] = url
            extracted_data["data_source"] = self._detect_source(url)

            return extracted_data

        except Exception as e:
            print(f"Error extracting with GPT: {e}")
            return None

    def _detect_source(self, url: str) -> str:
        """Detect listing source from URL."""
        if 'streeteasy.com' in url:
            return 'StreetEasy'
        elif 'zillow.com' in url:
            return 'Zillow'
        elif 'realtor.com' in url:
            return 'Realtor.com'
        else:
            return 'Other'

    def _map_to_airtable_format(self, data: Dict) -> Dict:
        """
        Map extracted data to Airtable field names and formats.

        Args:
            data: Extracted property data from GPT

        Returns:
            Dictionary formatted for Airtable
        """
        # Detect neighborhood from address
        neighborhood = self._detect_neighborhood(data.get('address', ''))

        airtable_data = {
            "Address": data.get("address"),
            "ListingURL": data.get("listing_url"),
            "CurrentPrice": data.get("price"),
            "OriginalPrice": data.get("price"),  # Same as current for new listings
            "PriceHistory": json.dumps([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "price": data.get("price")
            }]),
            "DaysOnMarket": 0,  # New listing
            "Bedrooms": data.get("bedrooms"),
            "Bathrooms": data.get("bathrooms"),
            "SQFT": data.get("sqft"),
            "MonthlyHOA": data.get("hoa_monthly"),
            "EstimatedMonthlyRent": data.get("estimated_rent"),
            "HasElevator": data.get("has_elevator", False),
            "HasDoorman": data.get("has_doorman", False),
            "HasParking": data.get("has_parking", False),
            "HasGym": data.get("has_gym", False),
            "HasRoofDeck": data.get("has_roof_deck", False),
            "PetFriendly": data.get("pet_friendly", False),
            "Exposure": data.get("exposure"),
            "FloorLevel": data.get("floor_level"),
            "FloorNumber": data.get("floor_number"),
            "SubwayDistance": data.get("subway_distance"),
            "NearestSubwayLines": data.get("nearest_subway_lines"),
            "YearBuilt": data.get("year_built"),
            "PropertyDescription": data.get("description"),
            "DataSource": data.get("data_source", "API"),
            "Status": "Active"
        }

        # Link to neighborhood if found
        if neighborhood:
            airtable_data["Neighborhood"] = [neighborhood]

        # Remove None values
        return {k: v for k, v in airtable_data.items() if v is not None}

    def _detect_neighborhood(self, address: str) -> Optional[str]:
        """
        Detect neighborhood from address string.

        Args:
            address: Full property address

        Returns:
            Airtable record ID for neighborhood, or None
        """
        # Common neighborhood patterns
        neighborhood_keywords = {
            "Long Island City": ["Long Island City", "LIC", "Queens", "11101", "11109"],
            "Hell's Kitchen": ["Hell's Kitchen", "Midtown West", "10019", "10036"],
            "DUMBO": ["DUMBO", "Brooklyn", "11201"],
            "Financial District": ["Financial District", "FiDi", "10005", "10004"],
            "Upper West Side": ["Upper West Side", "UWS", "10024", "10025"],
            "Park Slope": ["Park Slope", "Brooklyn", "11215"]
        }

        address_lower = address.lower()

        for neighborhood, keywords in neighborhood_keywords.items():
            if any(kw.lower() in address_lower for kw in keywords):
                # Find neighborhood record in Airtable
                try:
                    records = neighborhoods_table.all(
                        formula=f"{{NeighborhoodName}}='{neighborhood}'"
                    )
                    if records:
                        return records[0]['id']
                except Exception as e:
                    print(f"Error finding neighborhood: {e}")

        return None

    def add_to_airtable(self, property_data: Dict) -> Optional[str]:
        """
        Add property to Airtable database.

        Args:
            property_data: Extracted property data

        Returns:
            Airtable record ID if successful, None otherwise
        """
        airtable_formatted = self._map_to_airtable_format(property_data)

        try:
            record = properties_table.create(airtable_formatted)
            print(f"✓ Added property: {airtable_formatted.get('Address')}")
            return record['id']
        except Exception as e:
            print(f"✗ Error adding to Airtable: {e}")
            return None

    def process_listing_url(self, url: str) -> bool:
        """
        Complete pipeline: fetch, extract, and save property from URL.

        Args:
            url: Property listing URL

        Returns:
            True if successful, False otherwise
        """
        print(f"\nProcessing: {url}")

        # Fetch listing HTML
        html = self.fetch_listing_html(url)
        if not html:
            print("✗ Failed to fetch listing")
            return False

        # Extract text
        listing_text = self.extract_text_from_html(html)

        # Extract data with GPT
        property_data = self.extract_property_data_with_gpt(listing_text, url)
        if not property_data:
            print("✗ Failed to extract property data")
            return False

        # Add to Airtable
        record_id = self.add_to_airtable(property_data)
        if not record_id:
            return False

        print(f"✓ Successfully added property (Record ID: {record_id})")
        return True


def bulk_import_from_file(filepath: str):
    """
    Import multiple properties from a text file (one URL per line).

    Args:
        filepath: Path to file with listing URLs
    """
    extractor = PropertyExtractor()

    with open(filepath, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Processing {len(urls)} listings...")

    success_count = 0
    for url in urls:
        if extractor.process_listing_url(url):
            success_count += 1

    print(f"\n{'='*50}")
    print(f"Results: {success_count}/{len(urls)} properties added successfully")


def main():
    """Main execution function."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single URL:  python property_extractor.py <listing_url>")
        print("  Bulk import: python property_extractor.py --bulk <file_with_urls.txt>")
        return

    extractor = PropertyExtractor()

    if sys.argv[1] == '--bulk':
        if len(sys.argv) < 3:
            print("Error: Please provide file path for bulk import")
            return
        bulk_import_from_file(sys.argv[2])
    else:
        url = sys.argv[1]
        extractor.process_listing_url(url)


if __name__ == "__main__":
    main()
```
