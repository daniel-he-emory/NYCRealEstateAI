"""Quick script to load neighborhoods directly."""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

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
        "neighborhood_notes": "Growing waterfront neighborhood"
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
        "neighborhood_notes": "Vibrant Midtown West"
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
        "neighborhood_notes": "Waterfront with Manhattan views"
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
        "neighborhood_notes": "Historic downtown Manhattan"
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
        "neighborhood_notes": "Classic NYC neighborhood"
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
        "neighborhood_notes": "Family-friendly Brooklyn"
    }
]

print("Loading neighborhoods...")
try:
    result = supabase.table('neighborhoods').insert(neighborhoods).execute()
    print(f"✅ Loaded {len(result.data)} neighborhoods!")
    for n in result.data:
        print(f"  - {n.get('neighborhood_name', n.get('id'))}")
except Exception as e:
    error_msg = str(e)
    if "duplicate" in error_msg.lower():
        print("✅ Neighborhoods already loaded!")
    else:
        print(f"❌ Error: {e}")
