"""
Drop and recreate the chk_process_data_wip_serial_consistency constraint
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import text
from app.database import SessionLocal

db = SessionLocal()

try:
    print("Dropping old constraint...")
    db.execute(text("""
        ALTER TABLE process_data 
        DROP CONSTRAINT IF EXISTS chk_process_data_wip_serial_consistency;
    """))
    
    print("Creating new constraint (allowing WIP to have serial_id)...")
    db.execute(text("""
        ALTER TABLE process_data 
        ADD CONSTRAINT chk_process_data_wip_serial_consistency 
        CHECK (
            (data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR 
            (data_level = 'WIP' AND wip_id IS NOT NULL) OR 
            (data_level = 'SERIAL' AND serial_id IS NOT NULL)
        );
    """))
    
    db.commit()
    print("✅ Constraint updated successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
