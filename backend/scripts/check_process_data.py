"""
Check process_data table constraints and recent data using SQLAlchemy
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.process_data import ProcessData
from sqlalchemy import text

db = SessionLocal()

# Get all constraints on process_data table
print("=== CONSTRAINTS ON process_data TABLE ===")
result = db.execute(text("""
    SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'process_data'::regclass
    ORDER BY conname;
"""))
for row in result:
    print(f"{row[0]}: {row[1]}")

print("\n=== RECENT PROCESS_DATA RECORDS ===")
result = db.execute(text("""
    SELECT id, lot_id, process_id, started_at, completed_at, 
           duration_seconds, result, created_at
    FROM process_data 
    ORDER BY created_at DESC 
    LIMIT 5;
"""))
print("ID | Lot | Proc | Started | Completed | Duration | Result | Created")
for row in result:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")

print("\n=== IN-PROGRESS RECORDS (completed_at IS NULL) ===")
result = db.execute(text("""
    SELECT id, lot_id, process_id, started_at, completed_at, duration_seconds, result, data_level
    FROM process_data 
    WHERE completed_at IS NULL
    ORDER BY started_at DESC 
    LIMIT 5;
"""))
print("ID | Lot | Proc | Started | Completed | Duration | Result | Level")
for row in result:
    print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} | {row[6]} | {row[7]}")

db.close()
