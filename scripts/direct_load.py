"""
Direct data loader that bypasses schema cache issues.
"""

import os
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def insert_data(table, data):
    """Insert data directly via REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    response = requests.post(url, headers=headers, json=data)
    return response

print("="*70)
print("🚀 Direct Data Loader")
print("="*70)

# Step 1: Load Neighborhoods
print("\n📍 Loading neighborhoods...")

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

response = insert_data("neighborhoods", neighborhoods)
if response.status_code in [200, 201]:
    print(f"✅ Loaded {len(response.json())} neighborhoods!")
    neighborhood_map = {n['neighborhood_name']: n['id'] for n in response.json()}
else:
    # Maybe they already exist
    print(f"Response: {response.status_code}")
    if "duplicate" in response.text.lower():
        print("✅ Neighborhoods already exist, fetching IDs...")
        # Get existing neighborhoods
        get_url = f"{SUPABASE_URL}/rest/v1/neighborhoods?select=id,neighborhood_name"
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
        }
        response = requests.get(get_url, headers=headers)
        neighborhood_map = {n['neighborhood_name']: n['id'] for n in response.json()}
        print(f"✅ Found {len(neighborhood_map)} neighborhoods")
    else:
        print(f"Error: {response.text[:200]}")
        exit(1)

# Step 2: Generate and load properties
print("\n🏠 Generating 50 properties...")

NEIGHBORHOODS = {
    "Long Island City": {"borough": "Queens", "price_range": (700000, 2000000), "price_per_sqft": 1100},
    "Hell's Kitchen": {"borough": "Manhattan", "price_range": (1200000, 2500000), "price_per_sqft": 1400},
    "DUMBO": {"borough": "Brooklyn", "price_range": (1100000, 2200000), "price_per_sqft": 1500},
    "Financial District": {"borough": "Manhattan", "price_range": (900000, 2000000), "price_per_sqft": 1300},
    "Upper West Side": {"borough": "Manhattan", "price_range": (1300000, 3000000), "price_per_sqft": 1650},
    "Park Slope": {"borough": "Brooklyn", "price_range": (1000000, 2000000), "price_per_sqft": 1250}
}

properties = []

for i in range(50):
    neighborhood_name = random.choice(list(NEIGHBORHOODS.keys()))
    nbhd = NEIGHBORHOODS[neighborhood_name]

    beds = random.choice([1, 1, 2, 2, 2, 3, 3, 4])
    baths = beds if beds == 1 else random.choice([beds - 0.5, beds, beds + 0.5])
    sqft = 600 + (beds - 1) * 350 + random.randint(-100, 200)

    price_per_sqft = nbhd["price_per_sqft"] + random.randint(-150, 150)
    current_price = int(sqft * price_per_sqft / 1000) * 1000
    current_price = max(nbhd["price_range"][0], min(current_price, nbhd["price_range"][1]))

    has_price_cut = random.random() < 0.35
    if has_price_cut:
        cut_percent = random.uniform(3, 15)
        original_price = int(current_price / (1 - cut_percent/100))
        days_on_market = random.randint(45, 180)
    else:
        original_price = current_price
        days_on_market = random.randint(1, 60)

    price_history = [{
        "date": (datetime.now() - timedelta(days=days_on_market)).strftime("%Y-%m-%d"),
        "price": original_price
    }]
    # Don't JSON dumps it - send as dict for JSONB

    monthly_hoa = int(int(sqft * random.uniform(0.6, 1.2)) / 50) * 50
    estimated_rent = int((current_price * random.uniform(0.0032, 0.0045)) / 12 / 100) * 100

    property_data = {
        "address": f"{random.randint(100,999)} Test St #{random.randint(1,50)}{random.choice(['A','B','C'])}, {nbhd['borough']}, NY",
        "neighborhood_id": neighborhood_map.get(neighborhood_name),
        "current_price": current_price,
        "original_price": original_price,
        "price_history": price_history,  # Send as dict, not JSON string
        "days_on_market": days_on_market,
        "bedrooms": beds,
        "bathrooms": baths,
        "sqft": sqft,
        "monthly_hoa": monthly_hoa,
        "estimated_monthly_rent": estimated_rent,
        "has_elevator": random.random() < 0.85,
        "has_doorman": random.random() < 0.60,
        "has_gym": random.random() < 0.70,
        "has_parking": random.random() < 0.25,
        "pet_friendly": random.random() < 0.65,
        "exposure": random.choice(["North", "South", "East", "West", "Corner"]),
        "floor_level": random.choice(["Low (1-5)", "Mid (6-15)", "High (16-30)"]),
        "floor_number": random.randint(3, 30),
        "subway_distance": random.randint(3, 10),
        "year_built": random.randint(1950, 2023),
        "property_description": f"Beautiful {beds}BR/{baths}BA in {neighborhood_name}",
        "status": "Active",
        "estimated_annual_taxes": int(current_price * 0.01),
        "estimated_insurance": random.randint(1200, 2400),
        "down_payment": int(current_price * 0.20),
        "interest_rate": random.uniform(0.055, 0.075)
    }

    properties.append(property_data)

    if (i + 1) % 10 == 0:
        print(f"  Generated {i + 1}/50...")

print(f"✅ Generated {len(properties)} properties")

# Insert in batches
print("\n📤 Inserting properties...")
batch_size = 10
inserted = 0

for i in range(0, len(properties), batch_size):
    batch = properties[i:i + batch_size]
    response = insert_data("properties", batch)

    if response.status_code in [200, 201]:
        inserted += len(response.json())
        print(f"  Inserted {inserted}/{len(properties)}...")
    else:
        print(f"  Error at batch {i}: {response.status_code}")
        print(f"  {response.text[:200]}")

print(f"\n✅ Successfully loaded {inserted} properties!")

print("\n" + "="*70)
print("✅ ALL DONE!")
print("="*70)
print("\nNow run:")
print("  streamlit run app.py")
