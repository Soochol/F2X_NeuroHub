"""
Database migration: Add wip_id to process_data table

This migration adds WIP item tracking to ProcessData records,
enabling WIP-based dashboard metrics and real-time production monitoring.

Changes:
- Add wip_id column to process_data table
- Add foreign key constraint to wip_items table
- Add index on wip_id for query performance

Run this migration:
    python backend/database/migrations/add_wip_to_process_data.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text
from app.database import SessionLocal, engine


def upgrade():
    """Add wip_id column to process_data table."""
    print("Starting migration: Add wip_id to process_data")
    
    with engine.connect() as conn:
        # Add wip_id column
        print("  - Adding wip_id column...")
        conn.execute(text("""
            ALTER TABLE process_data 
            ADD COLUMN IF NOT EXISTS wip_id BIGINT;
        """))
        conn.commit()
        
        # Add foreign key constraint
        print("  - Adding foreign key constraint...")
        conn.execute(text("""
            ALTER TABLE process_data 
            ADD CONSTRAINT fk_process_data_wip 
            FOREIGN KEY (wip_id) 
            REFERENCES wip_items(id) 
            ON DELETE RESTRICT 
            ON UPDATE CASCADE;
        """))
        conn.commit()
        
        # Add index for performance
        print("  - Adding index on wip_id...")
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_process_data_wip 
            ON process_data(wip_id);
        """))
        conn.commit()
        
    print("Migration completed successfully!")


def downgrade():
    """Remove wip_id column from process_data table."""
    print("Starting rollback: Remove wip_id from process_data")
    
    with engine.connect() as conn:
        # Drop index
        print("  - Dropping index...")
        conn.execute(text("""
            DROP INDEX IF EXISTS idx_process_data_wip;
        """))
        conn.commit()
        
        # Drop foreign key constraint
        print("  - Dropping foreign key constraint...")
        conn.execute(text("""
            ALTER TABLE process_data 
            DROP CONSTRAINT IF EXISTS fk_process_data_wip;
        """))
        conn.commit()
        
        # Drop column
        print("  - Dropping wip_id column...")
        conn.execute(text("""
            ALTER TABLE process_data 
            DROP COLUMN IF EXISTS wip_id;
        """))
        conn.commit()
        
    print("Rollback completed successfully!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate process_data table to add wip_id")
    parser.add_argument(
        "--rollback", 
        action="store_true", 
        help="Rollback the migration (remove wip_id)"
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        confirm = input("Are you sure you want to rollback? This will remove the wip_id column. (yes/no): ")
        if confirm.lower() == "yes":
            downgrade()
        else:
            print("Rollback cancelled.")
    else:
        upgrade()
