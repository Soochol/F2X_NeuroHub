"""
Database migration script to add WIP data level support.
Executes the SQL migration using Python and SQLAlchemy.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

def run_migration():
    """Execute the WIP data level migration for SQLite."""
    
    print("Starting database migration...")
    print("=" * 60)
    print("Note: SQLite requires table recreation to modify constraints")
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                print("\n1. Creating backup of process_data table...")
                conn.execute(text(
                    "CREATE TABLE process_data_backup AS SELECT * FROM process_data"
                ))
                
                print("2. Dropping original process_data table...")
                conn.execute(text("DROP TABLE process_data"))
                
                print("3. Recreating process_data table with new constraints...")
                # Recreate table with updated constraints
                create_table_sql = """
                CREATE TABLE process_data (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    lot_id INTEGER NOT NULL,
                    serial_id INTEGER,
                    wip_id INTEGER,
                    process_id INTEGER NOT NULL,
                    operator_id INTEGER NOT NULL,
                    equipment_id INTEGER,
                    data_level VARCHAR(10) NOT NULL CHECK (data_level IN ('LOT', 'WIP', 'SERIAL')),
                    result VARCHAR(10) NOT NULL CHECK (result IN ('PASS', 'FAIL', 'REWORK')),
                    measurements JSON NOT NULL DEFAULT '{}',
                    defects JSON,
                    notes VARCHAR(1000),
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(lot_id) REFERENCES lots (id),
                    FOREIGN KEY(serial_id) REFERENCES serials (id),
                    FOREIGN KEY(wip_id) REFERENCES wip_items (id),
                    FOREIGN KEY(process_id) REFERENCES processes (id),
                    FOREIGN KEY(operator_id) REFERENCES users (id),
                    FOREIGN KEY(equipment_id) REFERENCES equipment (id),
                    CHECK (
                        (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR
                        (data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR
                        (data_level = 'SERIAL' AND serial_id IS NOT NULL)
                    ),
                    CHECK (completed_at IS NULL OR completed_at >= started_at)
                )
                """
                conn.execute(text(create_table_sql))
                
                print("4. Restoring data from backup...")
                conn.execute(text(
                    "INSERT INTO process_data SELECT * FROM process_data_backup"
                ))
                
                print("5. Dropping backup table...")
                conn.execute(text("DROP TABLE process_data_backup"))
                
                print("6. Recreating indexes...")
                indexes = [
                    "CREATE INDEX idx_process_data_lot ON process_data (lot_id)",
                    "CREATE INDEX idx_process_data_serial ON process_data (serial_id)",
                    "CREATE INDEX idx_process_data_wip ON process_data (wip_id)",
                    "CREATE INDEX idx_process_data_process ON process_data (process_id)",
                    "CREATE INDEX idx_process_data_operator ON process_data (operator_id)",
                    "CREATE INDEX idx_process_data_equipment ON process_data (equipment_id)",
                ]
                for idx_sql in indexes:
                    conn.execute(text(idx_sql))
                
                # Commit transaction
                trans.commit()
                
                print("\n✅ Migration completed successfully!")
                print("=" * 60)
                print("\nChanges applied:")
                print("  - Updated data_level constraint to include 'WIP'")
                print("  - Added wip_serial_consistency constraint")
                print("  - Recreated all indexes")
                print("\nYou can now use WIP IDs for process operations.")
                
            except Exception as e:
                print("\n⚠️  Rolling back transaction...")
                trans.rollback()
                raise
            
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        print("=" * 60)
        raise

if __name__ == "__main__":
    run_migration()
