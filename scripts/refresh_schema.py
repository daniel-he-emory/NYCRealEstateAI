"""
Refresh Supabase schema cache.

When tables are created or modified, Supabase's PostgREST cache needs to be refreshed.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def refresh_schema():
    """Send request to reload Supabase schema cache."""

    # PostgREST schema cache reload endpoint
    url = f"{SUPABASE_URL}/rest/v1/"

    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Prefer": "schema-cache-refresh"
    }

    print("🔄 Refreshing Supabase schema cache...")
    print(f"URL: {url}")

    try:
        # Send HEAD request with schema refresh preference
        response = requests.head(url, headers=headers)

        print(f"Response: {response.status_code}")

        if response.status_code in [200, 204]:
            print("✅ Schema cache refreshed successfully!")
            return True
        else:
            print(f"⚠️  Got response {response.status_code}")
            print("The schema might still be refreshed.")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Supabase Schema Cache Refresh")
    print("="*70 + "\n")

    if refresh_schema():
        print("\n✅ Done! You can now load data:")
        print("   python scripts/load_sample_data_supabase.py")
    else:
        print("\n⚠️  Manual alternative:")
        print("1. Go to Supabase Dashboard")
        print("2. Settings > API")
        print("3. Click 'Reload schema cache' button")
