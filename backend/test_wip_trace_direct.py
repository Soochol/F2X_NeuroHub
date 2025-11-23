"""
Direct test of the WIP trace endpoint to see the actual error
"""
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.wip_item import WIPItem
from app.models.process_data import ProcessData
from app.models.process import Process

# Create database session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("Testing WIP trace query...")
    print("=" * 60)
    
    # First, check if the WIP exists
    wip_id = "WIP-KR02PSA251101-003"
    print(f"\n1. Checking if WIP '{wip_id}' exists...")
    
    from app.crud import wip_item as crud
    wip_item = crud.get_by_wip_id(db, wip_id)
    
    if not wip_item:
        print(f"   ❌ WIP not found: {wip_id}")
        print("\n   Available WIPs:")
        all_wips = db.query(WIPItem).limit(5).all()
        for w in all_wips:
            print(f"      - {w.wip_id}")
    else:
        print(f"   ✅ WIP found: ID={wip_item.id}, wip_id={wip_item.wip_id}")
        
        # Now try the problematic query
        print(f"\n2. Testing process data query with join...")
        try:
            process_data_records = (
                db.query(ProcessData)
                .filter(ProcessData.wip_id == wip_item.id)
                .join(Process, ProcessData.process_id == Process.id)
                .order_by(Process.process_number, ProcessData.created_at)
                .all()
            )
            print(f"   ✅ Query successful! Found {len(process_data_records)} process data records")
            
            for pd in process_data_records[:3]:  # Show first 3
                print(f"      - Process: {pd.process.process_name if pd.process else 'N/A'}, Result: {pd.result}")
                
        except Exception as e:
            print(f"   ❌ Query failed with error:")
            print(f"      {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
    print("\n" + "=" * 60)
