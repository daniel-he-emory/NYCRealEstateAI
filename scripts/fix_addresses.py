"""
Clean up property addresses to be more readable.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("🔧 Cleaning up property addresses...")

# Get all properties
url = f"{SUPABASE_URL}/rest/v1/properties?select=id,address"
headers = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"
}

response = requests.get(url, headers=headers)
properties = response.json()

print(f"Found {len(properties)} properties to update")

# Borough name mapping
borough_map = {
    "1": "Manhattan",
    "2": "Bronx",
    "3": "Brooklyn",
    "4": "Queens",
    "5": "Staten Island"
}

updated = 0

for prop in properties:
    old_address = prop['address']

    # Parse format: '555 WEST 22ND STREET, 8BE, 1, NY 10011'
    parts = [p.strip() for p in old_address.split(',')]

    if len(parts) >= 4:
        building = parts[0].title()  # Title case
        unit = parts[1]
        borough_code = parts[2]
        city_zip = parts[3]

        # Get borough name
        borough = borough_map.get(borough_code, "Manhattan")

        # Reconstruct address
        new_address = f"{building}, Unit {unit}, {borough}, {city_zip}"

        # Update via API
        update_url = f"{SUPABASE_URL}/rest/v1/properties?id=eq.{prop['id']}"
        update_headers = {
            **headers,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        update_data = {"address": new_address}

        response = requests.patch(update_url, headers=update_headers, json=update_data)

        if response.status_code in [200, 204]:
            updated += 1
            if updated % 10 == 0:
                print(f"  Updated {updated}/{len(properties)}...")

print(f"\n✅ Updated {updated} addresses!")
print("\nAddresses now formatted as:")
print("  '555 West 22nd Street, Unit 8BE, Manhattan, NY 10011'")
print("\n🔄 Refresh your browser to see the updated addresses!")
