#!/usr/bin/env python3
"""
Fix database - drop and recreate tables properly
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("=" * 70)
print("Fixing Database Schema")
print("=" * 70)

client = create_client(SUPABASE_URL, SERVICE_KEY)

# Drop all tables in correct order (reverse of creation due to foreign keys)
drop_sql = """
-- Drop views first
DROP VIEW IF EXISTS active_listings CASCADE;
DROP VIEW IF EXISTS high_distress_properties CASCADE;
DROP VIEW IF EXISTS investment_opportunities CASCADE;

-- Drop tables in reverse order
DROP TABLE IF EXISTS buyer_search_matched_properties CASCADE;
DROP TABLE IF EXISTS buyer_search_neighborhoods CASCADE;
DROP TABLE IF EXISTS buyer_searches CASCADE;
DROP TABLE IF EXISTS market_metrics CASCADE;
DROP TABLE IF EXISTS historical_sales CASCADE;
DROP TABLE IF EXISTS comparable_sales CASCADE;
DROP TABLE IF EXISTS properties CASCADE;
DROP TABLE IF EXISTS neighborhoods CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS set_building_age() CASCADE;
"""

print("\n1. Dropping existing tables...")
try:
    # Use RPC to execute SQL (if available) or use direct SQL execution
    # For now, we'll print instructions
    print(drop_sql)
    print("\n⚠️  Please run the DROP statements above in Supabase SQL Editor first")
    print("Then run the complete migration SQL again")
    print("\nOR - let me try using the REST API...")

except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("Next Steps:")
print("=" * 70)
print("1. Go to: https://supabase.com/dashboard/project/uxjlxaengyhcgntgdjqn/sql/new")
print("2. Paste and run the DROP statements above")
print("3. Then paste and run the complete migration from COMPLETE_MIGRATION.sql")
