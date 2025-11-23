"""
Migration script to add partial unique index for restricting concurrent work.
Enforces that only one WIP item per LOT can be active (completed_at IS NULL) in a specific process.
"""
import sys
import os
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.config import settings

def migrate():
    print(f"Connecting to database: {settings.DATABASE_URL}")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Adding partial unique index: idx_process_data_single_active_per_lot")
        
        # Check if index exists first (to make it idempotent)
        # SQLite specific check
        if 'sqlite' in settings.DATABASE_URL:
            check_sql = text("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_process_data_single_active_per_lot'")
            result = conn.execute(check_sql).fetchone()
            if result:
                print("Index already exists. Skipping.")
                return
                
            # Create index
            # SQLite supports partial indexes
            sql = text("""
                CREATE UNIQUE INDEX idx_process_data_single_active_per_lot 
                ON process_data (lot_id, process_id) 
                WHERE completed_at IS NULL
            """)
            conn.execute(sql)
            print("Index created successfully (SQLite).")
            
        else:
            # PostgreSQL check
            check_sql = text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_process_data_single_active_per_lot'")
            result = conn.execute(check_sql).fetchone()
            if result:
                print("Index already exists. Skipping.")
                return

            # Create index
            sql = text("""
                CREATE UNIQUE INDEX idx_process_data_single_active_per_lot 
                ON process_data (lot_id, process_id) 
                WHERE completed_at IS NULL
            """)
            conn.execute(sql)
            print("Index created successfully (PostgreSQL).")
            
        conn.commit()
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
