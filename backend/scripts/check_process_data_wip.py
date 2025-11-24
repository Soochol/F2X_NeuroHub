"""Check ProcessData for the specific WIP item."""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.models.lot import Lot
from app.models.wip_item import WIPItem
from app.models.process_data import ProcessData
from sqlalchemy import and_

db = SessionLocal()

try:
    # Find the lot
    lot_number = "KR01A10251101"
    lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()
    
    if not lot:
        print(f"❌ LOT not found: {lot_number}")
        sys.exit(1)
    
    print(f"✅ Found LOT: {lot.lot_number} (ID: {lot.id})")
    print()
    
    # Find WIP item
    wip_id = "WIP-KR01A10251101-001"
    wip = db.query(WIPItem).filter(WIPItem.wip_id == wip_id).first()
    
    if not wip:
        print(f"❌ WIP not found: {wip_id}")
    else:
        print(f"✅ Found WIP: {wip.wip_id} (ID: {wip.id}, Status: {wip.status})")
    
    print()
    
    # Check ALL process data for this lot and process 1
    all_pd = db.query(ProcessData).filter(
        and_(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == 1
        )
    ).all()
    
    print(f"📊 ALL Process Data for LOT={lot.lot_number}, Process=1 ({len(all_pd)} records):")
    print("-" * 120)
    print(f"{'ID':<6} {'Data Level':<12} {'WIP ID':<10} {'Serial ID':<10} {'Result':<8} {'Started At':<20} {'Completed At':<20}")
    print("-" * 120)
    
    for pd in all_pd:
        started = str(pd.started_at)[:19] if pd.started_at else "None"
        completed = str(pd.completed_at)[:19] if pd.completed_at else "NOT COMPLETED"
        print(f"{pd.id:<6} {pd.data_level:<12} {str(pd.wip_id):<10} {str(pd.serial_id):<10} {pd.result:<8} {started:<20} {completed:<20}")
    
    print()
    
    # Find the in-progress one
    in_progress = db.query(ProcessData).filter(
        and_(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == 1,
            ProcessData.completed_at.is_(None)
        )
    ).all()
    
    print(f"⚠️  IN-PROGRESS Process Data ({len(in_progress)} records):")
    for pd in in_progress:
        print(f"  ID: {pd.id}")
        print(f"    data_level: {pd.data_level}")
        print(f"    wip_id: {pd.wip_id}")
        print(f"    serial_id: {pd.serial_id}")
        print(f"    result: {pd.result}")
        print(f"    started_at: {pd.started_at}")
        print(f"    completed_at: {pd.completed_at}")
        print()
        
        # THIS IS THE PROBLEM CHECK
        if pd.data_level == 'WIP' and pd.wip_id is None:
            print(f"  🚨 CONSTRAINT VIOLATION FOUND!")
            print(f"    ProcessData ID {pd.id} has:")
            print(f"      - data_level = 'WIP'")
            print(f"      - wip_id = NULL")
            print(f"    When trying to complete with result='PASS', database will reject because:")
            print(f"    Check constraint requires: (data_level = 'WIP' AND wip_id IS NOT NULL)")
            print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
