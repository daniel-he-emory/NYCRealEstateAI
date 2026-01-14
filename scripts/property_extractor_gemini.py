"""
NYC Real Estate Property Data Extractor (Gemini Flash Version)

This script extracts property information from listing URLs (StreetEasy, Zillow, etc.)
and adds them to the Supabase database using Google Gemini Flash for AI parsing.

Requirements:
    pip install google-generativeai requests beautifulsoup4 supabase python-dotenv
"""

import os
import json
import re
from typing import Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class PropertyExtractor:
    """Extract property data from listing URLs using Google Gemini Flash."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.neighborhood_ids = {}
        self._load_neighborhoods()

    def _load_neighborhoods(self):
        """Load neighborhood IDs from Supabase."""
        try:
            result = supabase.table('neighborhoods').select('id, neighborhood_name').execute()
            for record in result.data:
                self.neighborhood_ids[record['neighborhood_name']] = record['id']
            print(f"✓ Loaded {len(self.neighborhood_ids)} neighborhoods")
        except Exception as e:
            print(f"⚠️  Warning: Could not load neighborhoods: {e}")

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
        Extract clean text from HTML for Gemini processing.

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

        # Limit to first 5000 chars (Gemini can handle more than GPT)
        return text[:5000]

    def extract_property_data_with_gemini(self, listing_text: str, url: str) -> Optional[Dict]:
        """
        Use Gemini Flash to extract structured property data from listing text.

        Args:
            listing_text: Cleaned text from listing page
            url: Original listing URL

        Returns:
            Dictionary with extracted property data
        """
        prompt = f"""You are a property data extractor. Extract structured information from this real estate listing.

Return ONLY valid JSON with these exact fields:
{{
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
}}

IMPORTANT:
- Use null for missing values
- All prices/fees in dollars (not abbreviated)
- Be conservative with estimates
- For has_* fields, use true only if explicitly mentioned
- Return ONLY the JSON object, no other text

URL: {url}

Listing Content:
{listing_text}
"""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                )
            )

            # Extract JSON from response
            response_text = response.text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = re.sub(r'^```json?\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)

            extracted_data = json.loads(response_text)
            extracted_data["listing_url"] = url
            extracted_data["data_source"] = self._detect_source(url)

            return extracted_data

        except Exception as e:
            print(f"Error extracting with Gemini: {e}")
            print(f"Response: {response.text if 'response' in locals() else 'No response'}")
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

    def _map_to_supabase_format(self, data: Dict) -> Dict:
        """
        Map extracted data to Supabase field names and formats.

        Args:
            data: Extracted property data from Gemini

        Returns:
            Dictionary formatted for Supabase
        """
        # Detect neighborhood from address
        neighborhood_id = self._detect_neighborhood(data.get('address', ''))

        supabase_data = {
            "address": data.get("address"),
            "listing_url": data.get("listing_url"),
            "current_price": data.get("price"),
            "original_price": data.get("price"),  # Same as current for new listings
            "price_history": json.dumps([{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "price": data.get("price")
            }]),
            "days_on_market": 0,  # New listing
            "bedrooms": data.get("bedrooms"),
            "bathrooms": data.get("bathrooms"),
            "sqft": data.get("sqft"),
            "monthly_hoa": data.get("hoa_monthly"),
            "estimated_monthly_rent": data.get("estimated_rent"),
            "has_elevator": data.get("has_elevator", False),
            "has_doorman": data.get("has_doorman", False),
            "has_parking": data.get("has_parking", False),
            "has_gym": data.get("has_gym", False),
            "has_roof_deck": data.get("has_roof_deck", False),
            "pet_friendly": data.get("pet_friendly", False),
            "exposure": data.get("exposure"),
            "floor_level": data.get("floor_level"),
            "floor_number": data.get("floor_number"),
            "subway_distance": data.get("subway_distance"),
            "nearest_subway_lines": data.get("nearest_subway_lines"),
            "year_built": data.get("year_built"),
            "property_description": data.get("description"),
            "data_source": data.get("data_source", "API"),
            "status": "Active"
        }

        # Link to neighborhood if found
        if neighborhood_id:
            supabase_data["neighborhood_id"] = neighborhood_id

        # Remove None values
        return {k: v for k, v in supabase_data.items() if v is not None}

    def _detect_neighborhood(self, address: str) -> Optional[str]:
        """
        Detect neighborhood from address string.

        Args:
            address: Full property address

        Returns:
            Neighborhood UUID, or None
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
                return self.neighborhood_ids.get(neighborhood)

        return None

    def add_to_supabase(self, property_data: Dict) -> Optional[str]:
        """
        Add property to Supabase database.

        Args:
            property_data: Extracted property data

        Returns:
            Supabase record ID if successful, None otherwise
        """
        supabase_formatted = self._map_to_supabase_format(property_data)

        try:
            result = supabase.table('properties').insert(supabase_formatted).execute()
            print(f"✓ Added property: {supabase_formatted.get('address')}")
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            print(f"✗ Error adding to Supabase: {e}")
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

        # Extract data with Gemini
        property_data = self.extract_property_data_with_gemini(listing_text, url)
        if not property_data:
            print("✗ Failed to extract property data")
            return False

        # Add to Supabase
        record_id = self.add_to_supabase(property_data)
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
        print("NYC Real Estate AI - Property Extractor (Gemini Flash)")
        print("\nUsage:")
        print("  Single URL:  python property_extractor_gemini.py <listing_url>")
        print("  Bulk import: python property_extractor_gemini.py --bulk <file_with_urls.txt>")
        print("\nExample:")
        print("  python property_extractor_gemini.py https://streeteasy.com/building/...")
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
