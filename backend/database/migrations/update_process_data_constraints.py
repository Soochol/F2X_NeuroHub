"""
Migration to update process_data table constraints to support WIP data level
"""
import sqlite3
import sys

def upgrade():
    """Update constraints to support WIP data level"""
    conn = sqlite3.connect('dev.db')
    cursor = conn.cursor()
    
    try:
        print("Starting migration: Update process_data constraints for WIP support")
        
        # SQLite doesn't support ALTER TABLE to modify constraints
        # We need to recreate the table
        
        # Step 1: Rename existing table
        print("  - Renaming process_data to process_data_old...")
        cursor.execute("ALTER TABLE process_data RENAME TO process_data_old")
        
        # Step 2: Create new table with updated constraints
        print("  - Creating new process_data table with updated constraints...")
        cursor.execute("""
            CREATE TABLE process_data (
                id INTEGER NOT NULL,
                lot_id BIGINT NOT NULL,
                serial_id BIGINT,
                wip_id BIGINT,
                process_id BIGINT NOT NULL,
                operator_id BIGINT NOT NULL,
                equipment_id BIGINT,
                data_level VARCHAR(10) NOT NULL,
                result VARCHAR(10) NOT NULL,
                measurements JSON,
                defects JSON,
                notes TEXT,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                PRIMARY KEY (id),
                CONSTRAINT chk_process_data_data_level CHECK (data_level IN ('LOT', 'WIP', 'SERIAL')),
                CONSTRAINT chk_process_data_result CHECK (result IN ('PASS', 'FAIL', 'REWORK')),
                CONSTRAINT chk_process_data_wip_serial_consistency CHECK (
                    (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR
                    (data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR
                    (data_level = 'SERIAL' AND serial_id IS NOT NULL)
                ),
                CONSTRAINT chk_process_data_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
                CONSTRAINT chk_process_data_timestamps CHECK (completed_at IS NULL OR completed_at >= started_at),
                FOREIGN KEY(lot_id) REFERENCES lots (id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY(serial_id) REFERENCES serials (id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY(wip_id) REFERENCES wip_items (id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY(process_id) REFERENCES processes (id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY(operator_id) REFERENCES users (id) ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE SET NULL ON UPDATE CASCADE
            )
        """)
        
        # Step 3: Copy data from old table
        print("  - Copying data from old table...")
        cursor.execute("""
            INSERT INTO process_data 
            SELECT * FROM process_data_old
        """)
        
        # Step 4: Drop old table
        print("  - Dropping old table...")
        cursor.execute("DROP TABLE process_data_old")
        
        # Step 5: Recreate indexes
        print("  - Recreating indexes...")
        cursor.execute("CREATE INDEX idx_process_data_lot ON process_data(lot_id)")
        cursor.execute("CREATE INDEX idx_process_data_serial ON process_data(serial_id)")
        cursor.execute("CREATE INDEX idx_process_data_wip ON process_data(wip_id)")
        cursor.execute("CREATE INDEX idx_process_data_process ON process_data(process_id)")
        cursor.execute("CREATE INDEX idx_process_data_operator ON process_data(operator_id)")
        cursor.execute("CREATE INDEX idx_process_data_equipment ON process_data(equipment_id)")
        cursor.execute("CREATE INDEX idx_process_data_serial_process ON process_data(serial_id, process_id, result)")
        cursor.execute("CREATE INDEX idx_process_data_lot_process ON process_data(lot_id, process_id, result)")
        cursor.execute("CREATE INDEX idx_process_data_process_result ON process_data(process_id, result, started_at)")
        cursor.execute("CREATE INDEX idx_process_data_started_at ON process_data(started_at)")
        cursor.execute("CREATE INDEX idx_process_data_completed_at ON process_data(completed_at)")
        cursor.execute("CREATE INDEX idx_process_data_failed ON process_data(process_id, started_at)")
        cursor.execute("CREATE INDEX idx_process_data_data_level ON process_data(data_level, lot_id)")
        cursor.execute("CREATE INDEX idx_process_data_operator_performance ON process_data(operator_id, process_id, result, started_at)")
        cursor.execute("CREATE INDEX idx_process_data_equipment_utilization ON process_data(equipment_id, process_id, started_at)")
        
        # Step 6: Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade()
