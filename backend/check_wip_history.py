"""Check WIP process history"""
from app.database import SessionLocal
from app.models import WIPItem, WIPProcessHistory

db = SessionLocal()

wip = db.query(WIPItem).filter(WIPItem.wip_id == 'WIP-DT01A10251102-004').first()
if wip:
    print(f"WIP ID: {wip.wip_id}")
    print(f"WIP Status: {wip.status}")
    print(f"\nWIPProcessHistory records:")
    
    histories = db.query(WIPProcessHistory).filter(
        WIPProcessHistory.wip_item_id == wip.id
    ).all()
    
    print(f"Total: {len(histories)} records")
    for h in histories:
        print(f"  Process={h.process_id}, Result={h.result}, Started={h.started_at}, Completed={h.completed_at}")
else:
    print("WIP not found")

db.close()
