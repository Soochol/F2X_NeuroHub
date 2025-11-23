import sys
sys.path.append('.')

from app.database import SessionLocal
from app.crud import wip_item as crud

db = SessionLocal()

try:
    # Direct test
    print("Testing get_by_wip_id with  'WIP-KR02PSA251101-002'")
    wip = crud.get_by_wip_id(db, "WIP-KR02PSA251101-002")
    print(f"Result: {wip}")
    
    if wip:
        print(f"WIP ID: {wip.wip_id}, DB ID: {wip.id}")
    else:
        print("Not found")
        
        # Let's check what's in the database
        print("\nAll WIP items in database:")
        from app.models.wip_item import WIPItem
        all_wips = db.query(WIPItem).all()
        for w in all_wips:
            print(f"  ID: {w.id}, WIP ID: '{w.wip_id}'")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
