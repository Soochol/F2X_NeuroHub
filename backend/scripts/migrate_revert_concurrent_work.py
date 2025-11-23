"""
Migration script to drop the partial unique index `idx_process_data_single_active_per_lot`.
This reverts the restriction on concurrent work, allowing multiple WIP items from the same LOT
to be processed in the same process simultaneously.
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
        print("Dropping partial unique index: idx_process_data_single_active_per_lot")
        
        # Check if index exists
        if 'sqlite' in settings.DATABASE_URL:
            check_sql = text("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_process_data_single_active_per_lot'")
            result = conn.execute(check_sql).fetchone()
            if not result:
                print("Index does not exist. Skipping.")
                return
                
            # Drop index
            sql = text("DROP INDEX idx_process_data_single_active_per_lot")
            conn.execute(sql)
            print("Index dropped successfully (SQLite).")
            
        else:
            # PostgreSQL check
            check_sql = text("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_process_data_single_active_per_lot'")
            result = conn.execute(check_sql).fetchone()
            if not result:
                print("Index does not exist. Skipping.")
                return

            # Drop index
            sql = text("DROP INDEX idx_process_data_single_active_per_lot")
            conn.execute(sql)
            print("Index dropped successfully (PostgreSQL).")
            
        conn.commit()
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
