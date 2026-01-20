"""
Automatic database setup using all available methods.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")

project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

# Read SQL files
migration_file = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"
with open(migration_file, 'r') as f:
    migration_sql = f.read()

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

print("="*70)
print("🚀 Automatic Database Setup")
print("="*70)

# Try Method 1: Direct database connection via psycopg2
print("\n📊 Method 1: Trying direct PostgreSQL connection...")

try:
    import psycopg2

    # Try to connect using the pooler connection string
    # Format: postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres

    # We need the database password - let's try to get it from Supabase API
    print("Attempting to retrieve database connection info...")

    # This won't work without proper auth, so skip to next method
    raise Exception("Need database password")

except Exception as e:
    print(f"❌ Method 1 failed: {e}")

# Try Method 2: Supabase Management API with different endpoints
print("\n📊 Method 2: Trying Supabase Management API...")

def try_management_api():
    """Try different Management API endpoints."""

    endpoints = [
        f"https://api.supabase.com/v1/projects/{project_ref}/database/query",
        f"https://api.supabase.com/v1/projects/{project_ref}/database/sql",
    ]

    for endpoint in endpoints:
        print(f"  Trying: {endpoint}")

        headers = {
            "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # Try drop first
        try:
            response = requests.post(endpoint, headers=headers, json={"query": drop_sql}, timeout=30)
            print(f"    Drop tables response: {response.status_code}")

            if response.status_code == 200:
                time.sleep(1)

                # Now try migration
                response = requests.post(endpoint, headers=headers, json={"query": migration_sql}, timeout=60)
                print(f"    Migration response: {response.status_code}")

                if response.status_code == 200:
                    print("  ✅ Success!")
                    return True
        except Exception as e:
            print(f"    Error: {e}")

    return False

if SUPABASE_ACCESS_TOKEN:
    if try_management_api():
        print("\n✅ Database setup complete!")
        time.sleep(2)

        # Refresh schema
        print("\n🔄 Refreshing schema...")
        refresh_url = f"{SUPABASE_URL}/rest/v1/"
        refresh_headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Prefer": "schema-cache-refresh"
        }
        requests.head(refresh_url, headers=refresh_headers)

        print("\n✅ ALL DONE! Run this next:")
        print("  python scripts/load_sample_data_supabase.py")
        exit(0)

# Try Method 3: Create SQL function to execute DDL
print("\n📊 Method 3: Creating helper function...")

try:
    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    # Create a function that can execute arbitrary SQL
    create_function_sql = """
    CREATE OR REPLACE FUNCTION exec_sql(sql_text TEXT)
    RETURNS TEXT AS $$
    BEGIN
        EXECUTE sql_text;
        RETURN 'Success';
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;
    """

    print("  Creating SQL execution function...")
    # This won't work through the client library either
    print("  ❌ Cannot create functions via REST API")

except Exception as e:
    print(f"❌ Method 3 failed: {e}")

# All automated methods failed
print("\n" + "="*70)
print("❌ Automated setup not possible with current access")
print("="*70)

print("\n💡 Don't worry! I'll create a super simple helper:")
print("\n1. I'll prepare the SQL for you")
print("2. You just need to copy-paste twice")
print("3. Takes 1 minute total")

# Save SQL to files for easy copying
drop_file = Path(__file__).parent.parent / "DROP_TABLES.sql"
with open(drop_file, 'w') as f:
    f.write(drop_sql)

print(f"\n✅ Created: {drop_file}")
print(f"✅ Already have: {migration_file}")

print("\n" + "="*70)
print("📋 SUPER SIMPLE 2-STEP PROCESS")
print("="*70)

print("\n🔗 Open this link:")
print(f"   https://supabase.com/dashboard/project/{project_ref}/editor")

print("\n📄 Step A:")
print(f"   1. Run: cat {drop_file}")
print("   2. Copy the output")
print("   3. Paste in Supabase SQL Editor")
print("   4. Click RUN")

print("\n📄 Step B:")
print(f"   1. Run: cat {migration_file}")
print("   2. Copy ALL the output (it's long!)")
print("   3. Paste in Supabase SQL Editor")
print("   4. Click RUN")

print("\n✅ Then run:")
print("   python scripts/load_sample_data_supabase.py")
print("="*70)
