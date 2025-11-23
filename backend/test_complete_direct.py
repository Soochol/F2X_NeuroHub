"""
Direct test of complete_process logic to find the 500 error
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Lot, WIPItem, ProcessData, Process
from app.schemas.process_data import ProcessResult
from datetime import datetime

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("Testing complete_process logic...")
    print("=" * 70)
    
    # Simulate the PySide request
    lot_number = "WIP-KR02PSA251101-003"  # This is actually a WIP ID
    process_id = 1
    
    print(f"\n1. Smart Lookup for: {lot_number}")
    
    # Find LOT
    lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()
    
    if not lot:
        print(f"   LOT not found by lot_number, trying WIP ID...")
        
        if lot_number.startswith("WIP-"):
            wip = db.query(WIPItem).filter(WIPItem.wip_id == lot_number).first()
            if wip:
                print(f"   ✅ Found as WIP: {wip.wip_id}, LOT ID: {wip.lot_id}")
                lot = wip.lot
                wip_for_query = wip
            else:
                print(f"   ❌ WIP not found")
                exit(1)  
        else:
            print(f"   ❌ Not a WIP ID")
            exit(1)
    else:
        print(f"   ✅ Found as LOT: {lot.lot_number}")
        wip_for_query = None
    
    print(f"\n2. Finding in-progress ProcessData...")
    print(f"   Query: ProcessData where lot_id={lot.id}, процесс_id={process_id}, completed_at IS NULL")
    
    query = db.query(ProcessData).filter(
        ProcessData.lot_id == lot.id,
        ProcessData.process_id == process_id,
        ProcessData.completed_at.is_(None)
    )
    
    if wip_for_query:
        print(f"   Adding filter: wip_id={wip_for_query.id}")
        query = query.filter(ProcessData.wip_id == wip_for_query.id)
    
    process_data = query.first()
    
    if not process_data:
        print(f"   ❌ No in-progress process found!")
        
        # Check all ProcessData for this WIP
        all_pd = db.query(ProcessData).filter(ProcessData.wip_id == wip_for_query.id).all()
        print(f"\n   All ProcessData for WIP {wip_for_query.id}:")
        for pd in all_pd:
            print(f"      - ID: {pd.id}, Process: {pd.process_id}, Completed: {pd.completed_at}, Result: {pd.result}")
        exit(1)
    
    print(f"   ✅ Found ProcessData ID: {process_data.id}")
    print(f"      Started: {process_data.started_at}")
    print(f"      Completed: {process_data.completed_at}")
    
    print(f"\n3. Simulating completion update...")
    
    result = ProcessResult.PASS
    completed_at = datetime.utcnow()
    
    process_data.result = result
    process_data.completed_at = completed_at
    process_data.measurements = {}
    
    # Calculate duration
    duration_seconds = 0  # Initialize
    if process_data.started_at:
        start_ts = process_data.started_at
        end_ts = completed_at
        
        if start_ts.tzinfo and not end_ts.tzinfo:
            end_ts = end_ts.replace(tzinfo=start_ts.tzinfo)
        elif not start_ts.tzinfo and end_ts.tzinfo:
            start_ts = start_ts.replace(tzinfo=end_ts.tzinfo)
            
        duration_seconds = int((end_ts - start_ts).total_seconds())
        process_data.duration_seconds = duration_seconds
        print(f"   Duration calculated: {duration_seconds} seconds")
    else:
        process_data.duration_seconds = 0
        print(f"   No started_at, duration set to 0")
    
    print(f"\n4. Committing changes...")
    db.commit()
    db.refresh(process_data)
    
    print(f"   ✅ SUCCESS!")
    print(f"   Process completed at: {process_data.completed_at}")
    print(f"   Duration: {process_data.duration_seconds} seconds")
    print(f"   Result: {process_data.result}")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print("\n" + "=" * 70)
