"""Fix WIP data level constraints."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine

print("Fixing WIP data level constraints...")
print("=" * 60)

try:
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # 1. Drop incorrect constraints
            print("\n1. Dropping incorrect constraints...")
            conn.execute(text(
                "ALTER TABLE process_data DROP CONSTRAINT chk_process_data_data_level"
            ))
            conn.execute(text(
                "ALTER TABLE process_data DROP CONSTRAINT chk_process_data_serial_id"
            ))
            conn.execute(text(
                "ALTER TABLE process_data DROP CONSTRAINT chk_process_data_wip_serial_consistency"
            ))
            
            # 2. Add correct data_level constraint
            print("2. Adding correct data_level constraint...")
            conn.execute(text(
                "ALTER TABLE process_data ADD CONSTRAINT chk_process_data_data_level "
                "CHECK (data_level IN ('LOT', 'WIP', 'SERIAL'))"
            ))
            
            # 3. Add correct wip_serial_consistency constraint
            print("3. Adding correct wip_serial_consistency constraint...")
            conn.execute(text(
                "ALTER TABLE process_data ADD CONSTRAINT chk_process_data_wip_serial_consistency "
                "CHECK ("
                "(data_level = 'LOT' AND serial_id IS NULL AND wip_id IS NULL) OR "
                "(data_level = 'WIP' AND wip_id IS NOT NULL AND serial_id IS NULL) OR "
                "(data_level = 'SERIAL' AND serial_id IS NOT NULL)"
                ")"
            ))
            
            trans.commit()
            
            print("\n✅ Migration completed successfully!")
            print("=" * 60)
            print("\nChanges applied:")
            print("  - Updated data_level constraint to include 'WIP'")
            print("  - Fixed wip_serial_consistency constraint logic")
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
