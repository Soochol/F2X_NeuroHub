"""
Check actual process data for WIP-KR02PSA251101-003
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.process_data import ProcessData
from app.models.process import Process
from app.crud import wip_item as crud

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    wip_id = "WIP-KR02PSA251101-003"
    print(f"Checking process data for {wip_id}")
    print("=" * 70)
    
    # Get WIP
    wip_item = crud.get_by_wip_id(db, wip_id)
    if not wip_item:
        print(f"❌ WIP not found")
        exit(1)
    
    print(f"✅ WIP found: ID={wip_item.id}\n")
    
    # Get process data
    process_data_records = (
        db.query(ProcessData)
        .filter(ProcessData.wip_id == wip_item.id)
        .join(Process, ProcessData.process_id == Process.id)
        .order_by(Process.process_number, ProcessData.created_at)
        .all()
    )
    
    print(f"Found {len(process_data_records)} process data record(s):\n")
    
    for pd in process_data_records:
        print(f"Process {pd.process.process_number}: {pd.process.process_name_en}")
        print(f"  - Result: {pd.result}")
        print(f"  - Operator: {pd.operator.username if pd.operator else 'N/A'}")
        print(f"  - Started At: {pd.started_at}")
        print(f"  - Completed At: {pd.completed_at}")
        print(f"  - Duration: {pd.duration_seconds} seconds")
        print(f"  - Data Level: {pd.data_level}")
        print(f"  - Measurements: {pd.measurements}")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
