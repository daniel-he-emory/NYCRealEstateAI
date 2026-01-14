#!/usr/bin/env python3
"""
Automated migration runner using Supabase service role key
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def execute_sql(sql_content):
    """Execute SQL using Supabase REST API with service role key"""

    # Use the PostgREST rpc endpoint to execute raw SQL
    # Note: This requires creating a postgres function, so we'll use a different approach

    # Alternative: Use Supabase's SQL editor API
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"

    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }

    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    print(f"Found {len(statements)} SQL statements to execute")

    for i, statement in enumerate(statements, 1):
        if not statement:
            continue

        print(f"\nExecuting statement {i}/{len(statements)}...")
        print(f"Preview: {statement[:100]}...")

        # For now, we'll use psycopg2 approach
        # This won't work with just the service key
        # We need direct database connection

    return True

def main():
    print("=" * 60)
    print("NYC Real Estate AI - Automated Migration Runner")
    print("=" * 60)

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        print("❌ Error: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        sys.exit(1)

    print(f"✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ Service Role Key: {SERVICE_ROLE_KEY[:20]}...")

    # Read migration file
    migration_file = project_root / 'migrations' / '001_initial_schema.sql'

    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)

    print(f"✓ Reading migration: {migration_file.name}")

    with open(migration_file, 'r') as f:
        sql_content = f.read()

    print(f"✓ Loaded {len(sql_content)} characters of SQL")

    # Use psycopg2 with connection pooler
    import psycopg2

    # Extract project ref from URL
    project_ref = SUPABASE_URL.split('//')[1].split('.')[0]

    # Try to connect using service role (this might not work for DDL)
    # We need the database password for this
    print("\n" + "=" * 60)
    print("⚠️  Note: Direct SQL execution requires database password")
    print("=" * 60)
    print("\nUsing alternative approach: Supabase client library...")

    # Use supabase-py client
    from supabase import create_client

    client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

    # Split into manageable chunks and execute via RPC
    print("\n⚠️  Service role key alone cannot execute DDL statements.")
    print("We need to use PostgreSQL connection or Supabase Management API.")
    print("\nCreating helper RPC function...")

    return False

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n❌ Automated migration requires database password")
        print("\nPlease use one of these methods:")
        print("1. Run migration manually in Supabase SQL Editor")
        print("2. Provide database password for direct connection")
        sys.exit(1)
