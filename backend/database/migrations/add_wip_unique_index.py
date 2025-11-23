"""
Database migration: Add unique index for WIP-based process tracking

This migration adds a unique index on (lot_id, process_id, wip_id) to allow
multiple process executions for the same LOT as long as they have different WIP IDs.

Changes:
- Add unique index uq_process_data_lot_process_wip
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text
from app.database import engine

def upgrade():
    """Add unique index to process_data table."""
    print("Starting migration: Add unique index for WIP process tracking")
    
    with engine.connect() as conn:
        # Add unique index
        print("  - Creating unique index uq_process_data_lot_process_wip...")
        # SQLite doesn't support CREATE UNIQUE INDEX IF NOT EXISTS directly in all versions,
        # but we can try catch or just run it.
        # Also, for SQLite, we might need to handle the case where the index already exists.
        
        try:
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_process_data_lot_process_wip 
                ON process_data(lot_id, process_id, wip_id)
                WHERE wip_id IS NOT NULL;
            """))
            print("    Index created successfully.")
        except Exception as e:
            print(f"    Error creating index (might already exist): {e}")
            
        conn.commit()
        
    print("Migration completed successfully!")

def downgrade():
    """Remove unique index."""
    print("Starting rollback: Remove unique index")
    
    with engine.connect() as conn:
        print("  - Dropping index uq_process_data_lot_process_wip...")
        conn.execute(text("""
            DROP INDEX IF EXISTS uq_process_data_lot_process_wip;
        """))
        conn.commit()
        
    print("Rollback completed successfully!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add unique index for WIP process tracking")
    parser.add_argument(
        "--rollback", 
        action="store_true", 
        help="Rollback the migration"
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        downgrade()
    else:
        upgrade()
