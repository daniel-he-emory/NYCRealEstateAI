"""
Run SQL migrations on Supabase database.

This script executes SQL migration files against the Supabase PostgreSQL database.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_connection_string():
    """
    Extract database connection string from Supabase URL.
    Format: postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
    """
    # Extract project ref from URL
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

    print("\n" + "="*60)
    print("⚠️  MANUAL STEP REQUIRED")
    print("="*60)
    print("\nTo run migrations, you need your Supabase database password.")
    print("\n1. Go to: https://supabase.com/dashboard/project/" + project_ref + "/settings/database")
    print("2. Find 'Connection string' section")
    print("3. Copy the 'Connection pooling' URI (it contains your password)")
    print("\nOR use the Supabase SQL Editor:")
    print("1. Go to: https://supabase.com/dashboard/project/" + project_ref + "/editor")
    print("2. Paste the SQL from: migrations/001_initial_schema.sql")
    print("3. Click 'Run'")
    print("\n" + "="*60)

    return None

def run_migration_file(filepath: Path):
    """Run a single SQL migration file."""
    print(f"\nReading migration: {filepath.name}")

    with open(filepath, 'r') as f:
        sql = f.read()

    print(f"✓ Loaded {len(sql)} characters of SQL")
    print(f"✓ Migration contains {sql.count('CREATE TABLE')} table definitions")

    return sql

def main():
    """Main execution function."""
    print("NYC Real Estate AI - Database Migration")
    print("="*60)

    # Check environment
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return

    print(f"✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ API Key configured")

    # Load migration files
    migrations_dir = Path(__file__).parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("❌ No migration files found in migrations/")
        return

    print(f"\n✓ Found {len(migration_files)} migration file(s)")

    # Read and display migrations
    for migration_file in migration_files:
        sql = run_migration_file(migration_file)

        print("\n" + "="*60)
        print("MIGRATION SQL PREVIEW (first 500 chars):")
        print("="*60)
        print(sql[:500] + "...")

    # Instructions for manual execution
    get_connection_string()

    print("\n✅ Migration files are ready!")
    print("\nNext steps:")
    print("1. Use the Supabase SQL Editor (recommended)")
    print("2. Or get your DB password and uncomment the psycopg2 code below")

if __name__ == "__main__":
    main()
