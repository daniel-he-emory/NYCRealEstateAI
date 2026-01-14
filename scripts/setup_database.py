"""
Set up Supabase database with tables and sample data.

This script creates all tables and loads sample neighborhoods.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_connection(supabase: Client):
    """Test Supabase connection."""
    try:
        # Try to query a non-existent table (will fail gracefully if DB is empty)
        result = supabase.table('neighborhoods').select("*").limit(1).execute()
        print(f"✓ Connection successful! Found {len(result.data)} records in neighborhoods table")
        return True
    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "relation" in error_msg or "does not exist" in error_msg:
            print("✓ Connection successful! (Tables not yet created)")
            return True
        else:
            print(f"❌ Connection error: {e}")
            return False

def load_sample_neighborhoods(supabase: Client):
    """Load sample neighborhood data."""
    neighborhoods = [
        {
            "neighborhood_name": "Long Island City",
            "borough": "Queens",
            "median_price": 1200000,
            "median_price_per_sqft": 1100,
            "median_rent": 3800,
            "avg_days_on_market": 45,
            "price_change_yoy": 5.2,
            "avg_subway_access": 7,
            "walk_score": 92,
            "transit_score": 95,
            "neighborhood_notes": "Growing waterfront neighborhood with new luxury developments, excellent subway access via 7/E/M/G lines"
        },
        {
            "neighborhood_name": "Hell's Kitchen",
            "borough": "Manhattan",
            "median_price": 1600000,
            "median_price_per_sqft": 1400,
            "median_rent": 4500,
            "avg_days_on_market": 38,
            "price_change_yoy": 3.8,
            "avg_subway_access": 5,
            "walk_score": 98,
            "transit_score": 100,
            "neighborhood_notes": "Vibrant Midtown West location, restaurant scene, near theaters, excellent transit"
        },
        {
            "neighborhood_name": "DUMBO",
            "borough": "Brooklyn",
            "median_price": 1800000,
            "median_price_per_sqft": 1500,
            "median_rent": 5200,
            "avg_days_on_market": 42,
            "price_change_yoy": 4.5,
            "avg_subway_access": 6,
            "walk_score": 95,
            "transit_score": 92,
            "neighborhood_notes": "Waterfront neighborhood with iconic views of Manhattan, tech hub, family-friendly"
        },
        {
            "neighborhood_name": "Financial District",
            "borough": "Manhattan",
            "median_price": 1400000,
            "median_price_per_sqft": 1300,
            "median_rent": 4200,
            "avg_days_on_market": 50,
            "price_change_yoy": 2.1,
            "avg_subway_access": 7,
            "walk_score": 96,
            "transit_score": 98,
            "neighborhood_notes": "Historic downtown Manhattan, waterfront access, growing residential community"
        },
        {
            "neighborhood_name": "Upper West Side",
            "borough": "Manhattan",
            "median_price": 2000000,
            "median_price_per_sqft": 1650,
            "median_rent": 5500,
            "avg_days_on_market": 35,
            "price_change_yoy": 6.2,
            "avg_subway_access": 6,
            "walk_score": 99,
            "transit_score": 100,
            "neighborhood_notes": "Classic NYC neighborhood, Central Park, cultural institutions, excellent schools"
        },
        {
            "neighborhood_name": "Park Slope",
            "borough": "Brooklyn",
            "median_price": 1500000,
            "median_price_per_sqft": 1250,
            "median_rent": 4000,
            "avg_days_on_market": 40,
            "price_change_yoy": 5.8,
            "avg_subway_access": 8,
            "walk_score": 94,
            "transit_score": 90,
            "neighborhood_notes": "Family-friendly Brooklyn neighborhood, brownstones, Prospect Park, great dining"
        }
    ]

    try:
        result = supabase.table('neighborhoods').insert(neighborhoods).execute()
        print(f"✓ Loaded {len(result.data)} neighborhoods")
        return True
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg or "already exists" in error_msg:
            print("✓ Neighborhoods already loaded")
            return True
        else:
            print(f"❌ Error loading neighborhoods: {e}")
            return False

def show_migration_instructions():
    """Show instructions for running the SQL migration."""
    migration_file = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"

    print("\n" + "="*70)
    print("📋 MANUAL STEP: Create Database Tables")
    print("="*70)
    print("\nThe database tables need to be created via Supabase SQL Editor.")
    print("\n🔗 Open your Supabase SQL Editor:")
    print(f"   {SUPABASE_URL.replace('https://', 'https://supabase.com/dashboard/project/')}/editor")
    print("\n📄 Then:")
    print(f"   1. Open the file: {migration_file}")
    print("   2. Copy the entire SQL content")
    print("   3. Paste into Supabase SQL Editor")
    print("   4. Click 'Run' (or press Cmd/Ctrl + Enter)")
    print("\n⏱️  This will take ~5-10 seconds to create all tables.")
    print("="*70)

def main():
    """Main execution function."""
    print("\n🚀 NYC Real Estate AI - Supabase Setup")
    print("="*70)

    # Validate environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        print("\nCurrent .env status:")
        print(f"  SUPABASE_URL: {'✓ Set' if SUPABASE_URL else '❌ Missing'}")
        print(f"  SUPABASE_KEY: {'✓ Set' if SUPABASE_KEY else '❌ Missing'}")
        return False

    print(f"✓ Environment configured")
    print(f"  URL: {SUPABASE_URL}")
    print(f"  Key: {SUPABASE_KEY[:20]}...")

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

    # Test connection
    print("\n📡 Testing database connection...")
    if not test_connection(supabase):
        return False

    # Check if tables exist
    try:
        result = supabase.table('neighborhoods').select("count", count='exact').execute()
        print(f"\n✅ Tables exist! Found {result.count} neighborhoods")

        # Load sample data if empty
        if result.count == 0:
            print("\n📊 Loading sample neighborhood data...")
            load_sample_neighborhoods(supabase)
        else:
            print("✓ Sample data already loaded")

        # Show summary
        print("\n" + "="*70)
        print("✅ DATABASE READY!")
        print("="*70)
        print("\nYou can now:")
        print("  • Run: python scripts/generate_sample_data.py (create test properties)")
        print("  • Run: python scripts/property_extractor.py <url> (scrape listings)")
        print("  • Build the UI with Next.js or Lovable")

        return True

    except Exception as e:
        error_msg = str(e)
        if "Could not find the table" in error_msg or "relation" in error_msg or "does not exist" in error_msg:
            print("\n⚠️  Tables not found. Let's create them!")
            show_migration_instructions()
            print("\n💡 After running the SQL, run this script again to verify.")
            return False
        else:
            print(f"❌ Unexpected error: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
