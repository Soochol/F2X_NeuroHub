"""Check WIP data format in the database."""
import sys
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.models.lot import Lot
from app.models.wip_item import WIPItem
from app.models.process_data import ProcessData
from sqlalchemy import and_

db = SessionLocal()

try:
    # Find the lot - strip WIP- prefix if present
    lot_number_input = "WIP-KR01A10251101-001"
    lot_number = lot_number_input.replace("WIP-", "", 1)  # Remove WIP- prefix
    lot = db.query(Lot).filter(Lot.lot_number == lot_number).first()
    
    if not lot:
        print(f"❌ LOT not found: {lot_number}")
        sys.exit(1)
    
    print(f"✅ Found LOT: {lot.lot_number} (ID: {lot.id})")
    print()
    
    # Check WIP items for this lot
    wip_items = db.query(WIPItem).filter(WIPItem.lot_id == lot.id).all()
    print(f"📦 WIP Items for this LOT ({len(wip_items)} total):")
    print("-" * 80)
    
    for wip in wip_items[:10]:  # Show first 10
        print(f"  ID: {wip.id:4d} | wip_id: {wip.wip_id:30s} | Seq: {wip.sequence_in_lot:3d} | Status: {wip.status}")
    
    if len(wip_items) > 10:
        print(f"  ... and {len(wip_items) - 10} more")
    
    print()
    
    # Check if the specific WIP ID exists
    search_wip_id = f"WIP-{lot_number}"
    wip_exact = db.query(WIPItem).filter(WIPItem.wip_id == search_wip_id).first()
    
    if wip_exact:
        print(f"✅ Found exact match: {wip_exact.wip_id}")
    else:
        print(f"❌ No exact match for: {search_wip_id}")
        print()
        print("🔍 Trying pattern match...")
        wip_pattern = db.query(WIPItem).filter(WIPItem.wip_id.like(f"WIP-{lot_number}%")).all()
        if wip_pattern:
            print(f"   Found {len(wip_pattern)} WIP items matching pattern:")
            for w in wip_pattern[:5]:
                print(f"     - {w.wip_id}")
        else:
            print(f"   No WIP items found matching pattern WIP-{lot_number}%")
    
    print()
    
    # Check process_data for process 1
    process_data = db.query(ProcessData).filter(
        and_(
            ProcessData.lot_id == lot.id,
            ProcessData.process_id == 1,
            ProcessData.completed_at.is_(None)
        )
    ).all()
    
    print(f"🔧 Incomplete Process Data for Process 1 ({len(process_data)} records):")
    print("-" * 80)
    for pd in process_data[:5]:
        print(f"  ID: {pd.id:4d} | data_level: {pd.data_level:8s} | wip_id: {pd.wip_id} | serial_id: {pd.serial_id} | result: {pd.result}")
    
    if process_data and not process_data[0].wip_id and process_data[0].data_level == 'WIP':
        print()
        print("⚠️  FOUND THE PROBLEM!")
        print(f"   ProcessData ID {process_data[0].id} has data_level='WIP' but wip_id is NULL")
        print("   This will cause constraint violation when trying to complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
