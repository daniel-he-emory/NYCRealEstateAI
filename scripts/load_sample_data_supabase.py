"""
Load sample property data directly into Supabase.

This script generates realistic sample properties and inserts them
into the Supabase PostgreSQL database.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class SampleDataGenerator:
    """Generate realistic sample property data."""

    NEIGHBORHOODS = {
        "Long Island City": {
            "borough": "Queens",
            "subway_lines": ["7", "E", "M", "G"],
            "price_range": (700000, 2000000),
            "price_per_sqft": 1100,
            "subway_distance": (5, 10)
        },
        "Hell's Kitchen": {
            "borough": "Manhattan",
            "subway_lines": ["A", "C", "E", "1", "2", "3"],
            "price_range": (1200000, 2500000),
            "price_per_sqft": 1400,
            "subway_distance": (3, 8)
        },
        "DUMBO": {
            "borough": "Brooklyn",
            "subway_lines": ["A", "C", "F"],
            "price_range": (1100000, 2200000),
            "price_per_sqft": 1500,
            "subway_distance": (3, 7)
        },
        "Financial District": {
            "borough": "Manhattan",
            "subway_lines": ["2", "3", "4", "5", "J", "Z"],
            "price_range": (900000, 2000000),
            "price_per_sqft": 1300,
            "subway_distance": (5, 10)
        },
        "Upper West Side": {
            "borough": "Manhattan",
            "subway_lines": ["1", "2", "3", "B", "C"],
            "price_range": (1300000, 3000000),
            "price_per_sqft": 1650,
            "subway_distance": (4, 8)
        },
        "Park Slope": {
            "borough": "Brooklyn",
            "subway_lines": ["R", "M", "F", "G"],
            "price_range": (1000000, 2000000),
            "price_per_sqft": 1250,
            "subway_distance": (6, 10)
        }
    }

    EXPOSURES = ["North", "South", "East", "West", "Corner", "Multiple"]
    FLOOR_LEVELS = ["Low (1-5)", "Mid (6-15)", "High (16-30)", "Penthouse (31+)"]
    STATUSES = ["Active", "Price Change", "In Contract"]

    DESCRIPTIONS = [
        "Stunning {beds}BR/{baths}BA with floor-to-ceiling windows and breathtaking {neighborhood} views. Modern kitchen with high-end appliances, spa-like bathrooms, in-unit W/D.",
        "Spacious {beds}-bedroom apartment with {exposure} exposure and abundant natural light. Open chef's kitchen, hardwood floors throughout, generous closet space.",
        "Rarely available {beds}BR corner unit in prime {neighborhood}. High ceilings, renovated kitchen and baths, {amenities_desc}. Steps from subway and shopping.",
        "Mint condition {beds}BR with great light and city views. Open layout, modern finishes, {amenities_desc}. Building features excellent amenities.",
        "Classic {style} {beds}-bedroom with original details and modern updates. Hardwood floors, renovated kitchen, beautiful bathroom. Pet-friendly building.",
        "Contemporary {beds}BR/{baths}BA in luxury {neighborhood} building. Designer kitchen, spa bathroom, {amenities_desc}, breathtaking views."
    ]

    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.neighborhood_ids = {}

    def load_neighborhood_ids(self):
        """Load neighborhood IDs from Supabase."""
        try:
            result = self.supabase.table('neighborhoods').select('id, neighborhood_name').execute()
            for record in result.data:
                self.neighborhood_ids[record['neighborhood_name']] = record['id']
            print(f"✓ Loaded {len(self.neighborhood_ids)} neighborhood IDs")
        except Exception as e:
            print(f"⚠️  Warning: Could not load neighborhoods: {e}")

    def generate_property(self, neighborhood: str) -> Dict:
        """Generate a single realistic property listing."""

        nbhd_data = self.NEIGHBORHOODS[neighborhood]

        # Basic specs
        beds = random.choice([1, 1, 2, 2, 2, 3, 3, 4])  # Weighted towards 2-3BR
        baths = beds if beds == 1 else random.choice([beds - 0.5, beds, beds + 0.5])

        # Size and price
        base_sqft = 600 + (beds - 1) * 350 + random.randint(-100, 200)
        sqft = base_sqft
        price_per_sqft = nbhd_data["price_per_sqft"] + random.randint(-150, 150)
        current_price = int(sqft * price_per_sqft / 1000) * 1000  # Round to nearest 1k

        # Ensure price is in neighborhood range
        min_price, max_price = nbhd_data["price_range"]
        current_price = max(min_price, min(current_price, max_price))

        # Price history and distress signals
        has_price_cut = random.random() < 0.35  # 35% have price cuts
        if has_price_cut:
            cut_percent = random.uniform(3, 15)
            original_price = int(current_price / (1 - cut_percent/100))
            days_on_market = random.randint(45, 180)

            # Generate price history
            num_cuts = random.randint(1, 3)
            price_history = []
            price_step = (original_price - current_price) / num_cuts

            date = datetime.now() - timedelta(days=days_on_market)
            price_history.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": original_price
            })

            for i in range(1, num_cuts + 1):
                date += timedelta(days=random.randint(15, 45))
                price = int(original_price - (price_step * i))
                price_history.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": price
                })
        else:
            original_price = current_price
            days_on_market = random.randint(1, 60)
            price_history = [{
                "date": (datetime.now() - timedelta(days=days_on_market)).strftime("%Y-%m-%d"),
                "price": current_price
            }]

        # HOA fees
        base_hoa = int(sqft * random.uniform(0.6, 1.2))
        monthly_hoa = int(base_hoa / 50) * 50  # Round to nearest $50

        # Estimated rent
        rent_multiplier = random.uniform(0.0032, 0.0045)  # 3.2-4.5% annual yield
        estimated_rent = int((current_price * rent_multiplier) / 12 / 100) * 100  # Round to $100

        # Amenities
        has_elevator = random.random() < 0.85
        has_doorman = random.random() < 0.60
        has_parking = random.random() < 0.25
        has_gym = random.random() < 0.70
        has_roof_deck = random.random() < 0.55
        pet_friendly = random.random() < 0.65

        amenities = []
        if has_elevator:
            amenities.append("elevator")
        if has_doorman:
            amenities.append("24hr doorman")
        if has_gym:
            amenities.append("fitness center")
        if has_roof_deck:
            amenities.append("roof deck")

        # Floor and exposure
        floor_number = random.randint(3, 40)
        if floor_number <= 5:
            floor_level = "Low (1-5)"
        elif floor_number <= 15:
            floor_level = "Mid (6-15)"
        elif floor_number <= 30:
            floor_level = "High (16-30)"
        else:
            floor_level = "Penthouse (31+)"

        exposure = random.choice(self.EXPOSURES)

        # Subway
        subway_distance = random.randint(*nbhd_data["subway_distance"])
        subway_lines = ", ".join(random.sample(nbhd_data["subway_lines"],
                                               k=random.randint(1, min(3, len(nbhd_data["subway_lines"])))))

        # Building age
        year_built = random.randint(1920, 2023)
        style = "prewar" if year_built < 1945 else "modern"

        # Generate description
        amenities_desc = ", ".join(amenities) if amenities else "great amenities"
        description_template = random.choice(self.DESCRIPTIONS)
        description = description_template.format(
            beds=beds,
            baths=int(baths) if baths == int(baths) else baths,
            neighborhood=neighborhood,
            exposure=exposure.lower(),
            amenities_desc=amenities_desc,
            style=style
        )

        # Tags
        property_tags = []
        if year_built < 1945:
            property_tags.append("Prewar")
        if year_built >= 2015:
            property_tags.append("New Construction")
        if random.random() < 0.3:
            property_tags.append("Renovated")
        if random.random() < 0.2:
            property_tags.append("View")
        if random.random() < 0.15:
            property_tags.append("Outdoor Space")
        property_tags.append("In-Unit Laundry")

        # Status
        if has_price_cut and days_on_market > 30:
            status = "Price Change"
        elif random.random() < 0.1:
            status = "In Contract"
        else:
            status = "Active"

        # Generate address
        streets = {
            "Long Island City": [f"{random.randint(10,50)}-{random.randint(10,99)} {random.choice(['Center Blvd', '44th Dr', 'Jackson Ave', 'Vernon Blvd'])}"],
            "Hell's Kitchen": [f"West {random.randint(42, 57)}th St", f"{random.randint(400,600)} West {random.randint(42,57)}th St"],
            "DUMBO": [f"{random.randint(10,200)} {random.choice(['Water St', 'Front St', 'Jay St', 'Adams St'])}"],
            "Financial District": [f"{random.randint(10,200)} {random.choice(['Water St', 'Wall St', 'William St', 'Pearl St'])}"],
            "Upper West Side": [f"{random.randint(100,300)} West {random.randint(70,96)}th St"],
            "Park Slope": [f"{random.randint(100,500)} {random.choice(['5th', '6th', '7th', '8th'])} Avenue"]
        }
        street = random.choice(streets[neighborhood])
        unit = f"#{random.randint(1,50)}{random.choice(['A','B','C','D','E','F','G'])}"
        zip_codes = {
            "Long Island City": "11101",
            "Hell's Kitchen": "10019",
            "DUMBO": "11201",
            "Financial District": "10005",
            "Upper West Side": "10024",
            "Park Slope": "11215"
        }
        address = f"{street} {unit}, {nbhd_data['borough']}, NY {zip_codes[neighborhood]}"

        # Investment metrics (realistic estimates)
        estimated_taxes = int(current_price * 0.01)  # ~1% for condos in NYC
        estimated_insurance = random.randint(1200, 2400)
        estimated_utilities = random.randint(150, 300)
        property_management = int(estimated_rent * 0.08) if random.random() < 0.3 else 0

        down_payment = int(current_price * random.uniform(0.15, 0.30))
        interest_rate = random.uniform(0.055, 0.075)  # 5.5-7.5%

        # Build property dict (Supabase format)
        property_data = {
            "address": address,
            "neighborhood_id": self.neighborhood_ids.get(neighborhood),
            "listing_url": f"https://streeteasy.com/building/{street.replace(' ', '-').lower()}/{unit.lower()}",
            "current_price": current_price,
            "original_price": original_price,
            "price_history": json.dumps(price_history),
            "days_on_market": days_on_market,
            "bedrooms": beds,
            "bathrooms": baths,
            "sqft": sqft,
            "monthly_hoa": monthly_hoa,
            "estimated_monthly_rent": estimated_rent,
            "has_elevator": has_elevator,
            "has_doorman": has_doorman,
            "has_parking": has_parking,
            "has_gym": has_gym,
            "has_roof_deck": has_roof_deck,
            "pet_friendly": pet_friendly,
            "exposure": exposure,
            "floor_level": floor_level,
            "floor_number": floor_number,
            "subway_distance": subway_distance,
            "nearest_subway_lines": subway_lines,
            "year_built": year_built,
            "property_description": description,
            "property_tags": property_tags,
            "data_source": "StreetEasy",
            "status": status,
            "estimated_annual_taxes": estimated_taxes,
            "estimated_insurance": estimated_insurance,
            "estimated_utilities": estimated_utilities,
            "property_management_fee": property_management,
            "down_payment": down_payment,
            "interest_rate": interest_rate,
            "loan_term_years": 30
        }

        # Occasionally add last sale data
        if random.random() < 0.5:
            years_ago = random.randint(2, 8)
            last_sale_date = datetime.now() - timedelta(days=years_ago * 365)
            appreciation = random.uniform(0.10, 0.40)
            last_sale_price = int(current_price / (1 + appreciation))

            property_data.update({
                "last_sale_date": last_sale_date.strftime("%Y-%m-%d"),
                "last_sale_price": last_sale_price,
                "acris_record_id": f"{last_sale_date.strftime('%Y%m%d')}{random.randint(100000,999999)}"
            })

        return property_data

    def generate_and_load(self, count: int = 50):
        """Generate and load properties into Supabase."""
        print(f"\n🏗️  Generating {count} sample properties...")

        # Load neighborhood IDs first
        self.load_neighborhood_ids()

        if not self.neighborhood_ids:
            print("❌ No neighborhoods found. Please run the migration first.")
            return False

        properties = []
        neighborhoods = list(self.NEIGHBORHOODS.keys())

        for i in range(count):
            neighborhood = random.choice(neighborhoods)
            property_data = self.generate_property(neighborhood)
            properties.append(property_data)

            if (i + 1) % 10 == 0:
                print(f"  Generated {i + 1}/{count}...")

        print(f"✓ Generated {len(properties)} properties")

        # Insert into Supabase
        print(f"\n📤 Inserting into Supabase...")
        try:
            # Insert in batches of 10 to avoid timeouts
            batch_size = 10
            inserted = 0

            for i in range(0, len(properties), batch_size):
                batch = properties[i:i + batch_size]
                result = self.supabase.table('properties').insert(batch).execute()
                inserted += len(result.data)
                print(f"  Inserted {inserted}/{len(properties)}...")

            print(f"\n✅ Successfully loaded {inserted} properties!")
            return True

        except Exception as e:
            print(f"\n❌ Error inserting properties: {e}")
            return False


def main():
    """Main execution."""
    print("\n🚀 NYC Real Estate AI - Sample Data Loader")
    print("="*70)

    # Validate environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return False

    print(f"✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ API Key configured")

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

    # Generate and load data
    generator = SampleDataGenerator(supabase)

    # Ask for confirmation
    count = 50
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except:
            pass

    print(f"\n📊 Will generate {count} sample properties")
    confirm = input("Continue? (yes/no): ")

    if confirm.lower() != 'yes':
        print("Cancelled.")
        return False

    success = generator.generate_and_load(count)

    if success:
        print("\n" + "="*70)
        print("✅ SAMPLE DATA LOADED!")
        print("="*70)
        print("\nNext steps:")
        print("  • Run: streamlit run app.py (to view the data)")
        print("  • Or check Supabase dashboard to see your data")
        return True

    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
