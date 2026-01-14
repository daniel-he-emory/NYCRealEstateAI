#!/usr/bin/env python3
"""
Run migrations via Supabase RPC function
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("=" * 70)
print("NYC Real Estate AI - RPC-based Migration")
print("=" * 70)

# Create Supabase client with service role
client = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)

print("✓ Connected with service role key\n")

# First, create an RPC function that can execute arbitrary SQL
print("Step 1: Creating SQL execution helper function...")

create_exec_function_sql = """
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  EXECUTE query;
  RETURN 'Success';
EXCEPTION
  WHEN OTHERS THEN
    RETURN 'Error: ' || SQLERRM;
END;
$$;
"""

try:
    # Execute via SQL editor endpoint (this won't work without direct DB access)
    # Let's try a simpler approach - read and execute the SQL line by line

    print("Reading migration file...")
    migration_file = project_root / 'migrations' / '001_initial_schema.sql'
    with open(migration_file, 'r') as f:
        sql_content = f.read()

    print(f"✓ Loaded {len(sql_content)} characters")
    print("\n⚠️  Service role key cannot execute DDL directly via REST API")
    print("We need either:")
    print("  1. Database password for direct PostgreSQL connection")
    print("  2. Manual execution in Supabase SQL Editor")
    print("\nThe service role key is only for API operations, not schema changes.")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
