"""
Create error_logs table in the database.

This script creates the error_logs table and all necessary indexes using SQLAlchemy.
Run this script to initialize the error logging infrastructure.

Usage:
    python scripts/create_error_logs_table.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.error_log import ErrorLog
from app.models.user import User  # Import to create FK relationship


def create_tables():
    """Create error_logs table and indexes."""
    print("Creating error_logs table...")

    try:
        # Create all tables defined in Base metadata
        # This will only create tables that don't exist yet
        Base.metadata.create_all(bind=engine, tables=[ErrorLog.__table__])

        print("[SUCCESS] Successfully created error_logs table!")
        print(f"   - Table: {ErrorLog.__tablename__}")
        print(f"   - Columns: {', '.join([c.name for c in ErrorLog.__table__.columns])}")
        print(f"   - Indexes: {len(ErrorLog.__table__.indexes)} indexes created")

    except Exception as e:
        print(f"[ERROR] Error creating table: {e}")
        raise


if __name__ == "__main__":
    create_tables()
