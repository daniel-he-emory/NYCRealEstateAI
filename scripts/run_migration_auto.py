"""
Automatically run SQL migrations on Supabase using Management API.

This script executes the SQL migration file using Supabase's Management API
with the access token provided.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import time

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ACCESS_TOKEN = os.getenv("SUPABASE_ACCESS_TOKEN")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_project_ref():
    """Extract project reference from Supabase URL."""
    return SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

def execute_sql_via_management_api(sql: str):
    """
    Execute SQL using Supabase Management API.

    Uses the access token to execute SQL via the Management API's SQL endpoint.
    """
    project_ref = get_project_ref()

    # Supabase Management API endpoint for SQL execution
    api_url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"

    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": sql
    }

    print(f"\n🌐 Executing SQL via Supabase Management API...")
    print(f"Endpoint: {api_url}")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)

        if response.status_code == 200:
            print("✅ SQL executed successfully!")
            return True
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def verify_tables_exist():
    """Verify that tables were created successfully."""
    try:
        from supabase import create_client, Client

        # Use service role key for admin access
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

        print("\n🔍 Verifying tables were created...")

        tables = ['neighborhoods', 'properties', 'comparable_sales', 'historical_sales', 'market_metrics', 'buyer_searches']
        all_exist = True

        for table in tables:
            try:
                result = supabase.table(table).select("*").limit(1).execute()
                print(f"  ✓ {table}")
            except Exception as e:
                error_msg = str(e).lower()
                if "does not exist" in error_msg or "relation" in error_msg:
                    print(f"  ✗ {table} - NOT FOUND")
                    all_exist = False
                else:
                    print(f"  ? {table} - error checking")

        if all_exist:
            print("\n✅ All tables verified!")
        return all_exist

    except Exception as e:
        print(f"\n❌ Error verifying tables: {e}")
        return False

def read_migration_file():
    """Read the SQL migration file."""
    migration_file = Path(__file__).parent.parent / "migrations" / "001_initial_schema.sql"

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return None

    with open(migration_file, 'r') as f:
        sql = f.read()

    print(f"✓ Loaded migration file ({len(sql):,} characters)")
    print(f"✓ Contains {sql.count('CREATE TABLE')} table definitions")

    return sql

def main():
    """Main execution."""
    print("\n" + "="*70)
    print("🚀 NYC Real Estate AI - Automatic Migration")
    print("="*70)

    # Validate environment
    if not SUPABASE_URL:
        print("❌ Error: SUPABASE_URL must be set in .env")
        return False

    if not SUPABASE_ACCESS_TOKEN and not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: Need SUPABASE_ACCESS_TOKEN or SUPABASE_SERVICE_ROLE_KEY")
        return False

    project_ref = get_project_ref()
    print(f"\n✓ Project: {project_ref}")
    print(f"✓ URL: {SUPABASE_URL}")

    if SUPABASE_ACCESS_TOKEN:
        print(f"✓ Access token configured ({SUPABASE_ACCESS_TOKEN[:20]}...)")
    if SUPABASE_SERVICE_ROLE_KEY:
        print(f"✓ Service role key configured")

    # Check if tables already exist
    print("\n" + "-"*70)
    print("Checking existing tables...")
    print("-"*70)

    if verify_tables_exist():
        print("\n✅ Tables already exist! No migration needed.")
        print("\nYou can now run:")
        print("  python scripts/load_sample_data_supabase.py")
        return True

    print("\n📋 Tables not found. Running migration...\n")

    # Read migration file
    sql = read_migration_file()
    if not sql:
        return False

    # Try Management API method
    if SUPABASE_ACCESS_TOKEN:
        print("\n" + "-"*70)
        print("Method: Supabase Management API")
        print("-"*70)

        if execute_sql_via_management_api(sql):
            # Wait a moment for tables to be created
            print("\n⏳ Waiting for tables to be created...")
            time.sleep(3)

            # Verify
            if verify_tables_exist():
                print("\n" + "="*70)
                print("✅ MIGRATION COMPLETE!")
                print("="*70)
                print("\nNext steps:")
                print("  1. Load sample data:")
                print("     python scripts/load_sample_data_supabase.py")
                print("\n  2. Launch demo:")
                print("     streamlit run app.py")
                return True
            else:
                print("\n⚠️  SQL executed but tables not found. Checking again...")
                time.sleep(2)
                if verify_tables_exist():
                    print("✅ Tables created successfully!")
                    return True

    # If API method failed, show manual instructions
    print("\n" + "="*70)
    print("📋 MANUAL MIGRATION (Alternative)")
    print("="*70)
    print("\nIf automated migration didn't work, you can:")
    print("\n1. Open Supabase SQL Editor:")
    print(f"   https://supabase.com/dashboard/project/{project_ref}/editor")
    print("\n2. Copy contents of:")
    print("   migrations/001_initial_schema.sql")
    print("\n3. Paste into SQL Editor and click 'RUN'")
    print("\n4. Then run: python scripts/load_sample_data_supabase.py")
    print("="*70)

    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
