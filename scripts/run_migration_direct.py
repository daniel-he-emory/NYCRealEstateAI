#!/usr/bin/env python3
"""
Run migration using direct database connection
"""
import sys
from pathlib import Path
import psycopg2

project_root = Path(__file__).parent.parent

# Connection parameters
conn_params = {
    'host': 'db.uxjlxaengyhcgntgdjqn.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': '2513@fuhefuhE',
    'sslmode': 'require'
}

print("=" * 70)
print("NYC Real Estate AI - Direct Database Migration")
print("=" * 70)
print("\n✓ Connecting to Supabase database...")

try:
    # Connect to database
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    print("✓ Connected successfully!\n")

    # Read migration file
    print("=" * 70)
    print("Running Main Migration")
    print("=" * 70)

    migration_file = project_root / 'migrations' / '001_initial_schema.sql'
    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print(f"✓ Loaded {len(migration_sql)} characters of SQL")
    print("✓ Executing migration...\n")

    cursor.execute(migration_sql)
    conn.commit()

    print("✓ Main migration completed!\n")

    # Add building_age trigger
    print("=" * 70)
    print("Adding Building Age Trigger")
    print("=" * 70)

    building_age_sql = """
ALTER TABLE properties ADD COLUMN IF NOT EXISTS building_age INTEGER;

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

DROP TRIGGER IF EXISTS set_building_age_trigger ON properties;
CREATE TRIGGER set_building_age_trigger
  BEFORE INSERT OR UPDATE ON properties
  FOR EACH ROW
  EXECUTE FUNCTION set_building_age();
"""

    cursor.execute(building_age_sql)
    conn.commit()

    print("✓ Building age trigger added!\n")

    # Verify tables
    print("=" * 70)
    print("Verifying Database Schema")
    print("=" * 70)

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    tables = cursor.fetchall()
    print(f"\n✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 70)
    print("✅ DATABASE MIGRATION COMPLETE!")
    print("=" * 70)
    print("\nAll tables, triggers, and views have been created successfully!")
    print("\nNext: Loading sample data...")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
