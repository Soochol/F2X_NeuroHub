"""
Reset Database Script for F2X NeuroHub MES.

This script completely resets the database by truncating all tables
and resetting sequences. Use with caution!

Usage:
    python backend/scripts/reset_database.py
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import text
from app.database import SessionLocal


def reset_database():
    """Reset all data and sequences in the database."""
    print("\n" + "=" * 60)
    print("F2X NeuroHub MES - Database Reset")
    print("=" * 60)
    print("WARNING: This will delete ALL data from the database!")
    print("=" * 60 + "\n")

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("Operation cancelled.")
        return

    db = SessionLocal()

    try:
        print("\nDisabling triggers...")
        # Disable triggers temporarily
        db.execute(text("SET session_replication_role = 'replica';"))

        print("Truncating tables...")
        # Truncate tables in reverse dependency order
        tables = [
            "wip_process_history",
            "process_data",
            "wip_items",
            "serials",
            "lots",
            "equipment",
            "production_lines",
            "product_models",
            # Keep users and processes as they're master data
        ]

        for table in tables:
            print(f"  - Truncating {table}...")
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))

        print("Re-enabling triggers...")
        db.execute(text("SET session_replication_role = 'origin';"))

        db.commit()
        print("\n" + "=" * 60)
        print("Database reset completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        db.rollback()
        print(f"\nError resetting database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()
