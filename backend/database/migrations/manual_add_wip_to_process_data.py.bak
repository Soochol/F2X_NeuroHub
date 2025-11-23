"""
Manual SQL migration script for adding wip_id to process_data table.

This script connects to the database and executes the migration SQL directly.
Use this if the automated migration script fails due to connection issues.
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy import text
from app.database import SessionLocal


def run_migration():
    """Execute SQL migration to add wip_id column."""
    print("=" * 80)
    print("Manual Migration: Add wip_id to process_data")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Step 1: Add wip_id column
        print("\n[1/3] Adding wip_id column to process_data table...")
        db.execute(text("""
            ALTER TABLE process_data 
            ADD COLUMN IF NOT EXISTS wip_id BIGINT;
        """))
        db.commit()
        print("✓ Column added successfully")
        
        # Step 2: Add foreign key constraint
        print("\n[2/3] Adding foreign key constraint...")
        db.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint 
                    WHERE conname = 'fk_process_data_wip'
                ) THEN
                    ALTER TABLE process_data 
                    ADD CONSTRAINT fk_process_data_wip 
                    FOREIGN KEY (wip_id) 
                    REFERENCES wip_items(id) 
                    ON DELETE RESTRICT 
                    ON UPDATE CASCADE;
                END IF;
            END $$;
        """))
        db.commit()
        print("✓ Foreign key constraint added successfully")
        
        # Step 3: Add index
        print("\n[3/3] Adding index on wip_id...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_process_data_wip 
            ON process_data(wip_id);
        """))
        db.commit()
        print("✓ Index created successfully")
        
        print("\n" + "=" * 80)
        print("Migration completed successfully! ✓")
        print("=" * 80)
        
        # Verify the changes
        print("\nVerifying migration...")
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'process_data' AND column_name = 'wip_id';
        """))
        row = result.fetchone()
        if row:
            print(f"✓ Column 'wip_id' exists with type: {row[1]}")
        else:
            print("⚠ Warning: Could not verify column creation")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Database credentials in .env are correct")
        print("3. You have permission to alter tables")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
