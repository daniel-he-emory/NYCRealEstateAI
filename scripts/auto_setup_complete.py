#!/usr/bin/env python3
"""
Fully automated setup script - runs all migrations and loads data
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
DB_PASSWORD = "2513@fuhefuhE"

# Extract project ref from URL
project_ref = SUPABASE_URL.split('//')[1].split('.')[0]

# Supabase connection string format (using pooler for IPv4)
DB_HOST = f"aws-0-us-east-1.pooler.supabase.com"
DB_NAME = "postgres"
DB_USER = f"postgres.{project_ref}"
DB_PORT = 5432  # Session mode pooler

print("=" * 70)
print("NYC Real Estate AI - FULLY AUTOMATED SETUP")
print("=" * 70)
print(f"\n✓ Connecting to database: {DB_HOST}")
print(f"✓ Database: {DB_NAME}")
print(f"✓ User: {DB_USER}\n")

try:
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'
    )
    conn.autocommit = False
    cursor = conn.cursor()

    print("✓ Connected to Supabase PostgreSQL!\n")

    # Step 1: Run main migration
    print("=" * 70)
    print("STEP 1: Running main migration (001_initial_schema.sql)")
    print("=" * 70)

    migration_file = project_root / 'migrations' / '001_initial_schema.sql'
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print(f"✓ Loaded {len(migration_sql)} characters of SQL")
    print("✓ Executing migration...")

    cursor.execute(migration_sql)
    conn.commit()

    print("✓ Main migration completed successfully!\n")

    # Step 2: Add building_age trigger
    print("=" * 70)
    print("STEP 2: Adding building_age trigger")
    print("=" * 70)

    building_age_sql = """
-- Add nullable building_age column
ALTER TABLE properties ADD COLUMN IF NOT EXISTS building_age INTEGER;

-- Trigger function to set building_age using CURRENT_DATE
CREATE OR REPLACE FUNCTION set_building_age()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.year_built IS NOT NULL THEN
    NEW.building_age := EXTRACT(YEAR FROM CURRENT_DATE)::integer - NEW.year_built;
  ELSE
    NEW.building_age := NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS set_building_age_trigger ON properties;
CREATE TRIGGER set_building_age_trigger
  BEFORE INSERT OR UPDATE ON properties
  FOR EACH ROW
  EXECUTE FUNCTION set_building_age();
"""

    cursor.execute(building_age_sql)
    conn.commit()

    print("✓ Building age trigger added successfully!\n")

    # Step 3: Verify tables exist
    print("=" * 70)
    print("STEP 3: Verifying database schema")
    print("=" * 70)

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()
    print(f"✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Load sample data (run setup_database.py)")
    print("2. Launch Streamlit app")

except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    print(f"\nError details: {e.pgerror}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
