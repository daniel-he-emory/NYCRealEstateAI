"""
Drop existing tables and run fresh migration.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

def execute_sql(sql):
    """Execute SQL via Management API."""
    url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"

    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {"query": sql}

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    return response

print("🗑️  Dropping existing tables...")

# Drop all tables
drop_sql = """
DROP TABLE IF EXISTS buyer_search_matched_properties CASCADE;
DROP TABLE IF EXISTS buyer_search_neighborhoods CASCADE;
DROP TABLE IF EXISTS buyer_searches CASCADE;
DROP TABLE IF EXISTS market_metrics CASCADE;
DROP TABLE IF EXISTS historical_sales CASCADE;
DROP TABLE IF EXISTS comparable_sales CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS neighborhoods CASCADE;
"""

response = execute_sql(drop_sql)
if response.status_code == 200:
    print("✅ Tables dropped")
else:
    print(f"⚠️  Drop response: {response.status_code} - {response.text[:200]}")

print("\n⏳ Waiting 2 seconds...")
time.sleep(2)

print("\n🏗️  Running fresh migration...")

# Read migration
migration_file = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"
with open(migration_file, 'r') as f:
    migration_sql = f.read()

response = execute_sql(migration_sql)

if response.status_code == 200:
    print("✅ Migration executed successfully!")
    print("\n⏳ Waiting for schema to propagate...")
    time.sleep(3)

    # Refresh schema cache
    print("\n🔄 Refreshing schema cache...")
    refresh_url = f"{SUPABASE_URL}/rest/v1/"
    refresh_headers = {
        "apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
        "Prefer": "schema-cache-refresh"
    }
    requests.head(refresh_url, headers=refresh_headers)
    print("✅ Schema refreshed")

    print("\n✅ Database reset complete!")
    print("\nYou can now run:")
    print("  python scripts/load_sample_data_supabase.py")

else:
    print(f"❌ Migration failed: {response.status_code}")
    print(response.text[:500])
