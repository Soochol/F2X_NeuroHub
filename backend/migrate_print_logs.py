"""
Create print_logs table for tracking label printing history
"""
from app.database import engine
from sqlalchemy import text

def run_migration():
    conn = engine.connect()
    
    # Create print_logs table
    try:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS print_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label_type VARCHAR(50) NOT NULL,
                label_id VARCHAR(255) NOT NULL,
                process_id INTEGER,
                process_data_id INTEGER,
                printer_ip VARCHAR(50),
                printer_port INTEGER,
                status VARCHAR(20) NOT NULL,
                error_message TEXT,
                operator_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (process_id) REFERENCES processes(id),
                FOREIGN KEY (process_data_id) REFERENCES process_data(id),
                FOREIGN KEY (operator_id) REFERENCES users(id)
            )
        """))
        print("✅ Created print_logs table")
    except Exception as e:
        print(f"⚠️  print_logs table might already exist: {e}")
    
    # Create indexes
    try:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_print_logs_label_type ON print_logs(label_type)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_print_logs_created_at ON print_logs(created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_print_logs_status ON print_logs(status)"))
        print("✅ Created indexes on print_logs")
    except Exception as e:
        print(f"⚠️  Indexes might already exist: {e}")
    
    conn.commit()
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
