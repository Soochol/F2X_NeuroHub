"""
Database migration script to add WIP data level support for PostgreSQL.
Executes the SQL migration using Python and SQLAlchemy.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, is_postgresql

def run_migration():
    """Execute the WIP data level migration for PostgreSQL."""
    
    if not is_postgresql():
        print("❌ This migration is for PostgreSQL only!")
        print(f"Current DATABASE_URL uses SQLite.")
        print("\nPlease update .env file:")
        print("DATABASE_URL=postgresql://postgres:postgres@localhost:5432/f2x_neurohub")
        return
    
    print("Starting PostgreSQL database migration...")
    print("=" * 60)
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # 1. Drop old constraints
                print("\n1. Dropping old constraints...")
                conn.execute(text(
                    "ALTER TABLE process_data DROP CONSTRAINT IF EXISTS chk_process_data_data_level"
                ))
                conn.execute(text(
                    "ALTER TABLE process_data DROP CONSTRAINT IF EXISTS chk_process_data_serial_id"
                ))
                
                # 2. Add new data_level constraint
                print("2. Adding new data_level constraint...")
                conn.execute(text(
                    "ALTER TABLE process_data ADD CONSTRAINT chk_process_data_data_level "
                    "CHECK (data_level IN ('LOT', 'WIP', 'SERIAL'))"
                ))
                
                # 3. Add new wip_serial_consistency constraint
                print("3. Adding wip_serial_consistency constraint...")
                conn.execute(text(
                    "ALTER TABLE process_data ADD CONSTRAINT chk_process_data_wip_serial_consistency "
                    "CHECK ("
                    "(data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR "
                    "(data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR "
                    "(data_level = 'SERIAL' AND serial_id IS NOT NULL)"
                    ")"
                ))
                
                # Commit transaction
                trans.commit()
                
                print("\n✅ Migration completed successfully!")
                print("=" * 60)
                print("\nChanges applied:")
                print("  - Updated data_level constraint to include 'WIP'")
                print("  - Added wip_serial_consistency constraint")
                print("\nYou can now use WIP IDs for process operations.")
                
            except Exception as e:
                print("\n⚠️  Rolling back transaction...")
                trans.rollback()
                raise
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run_migration()
