import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal
from app.api.v1.wip_items import get_wip_trace
from app.crud import user as user_crud

# Create database session
db = SessionLocal()

try:
    # Get admin user
    admin = user_crud.get_by_username(db, username="admin")
    if not admin:
        print("Admin user not found!")
        sys.exit(1)
    
    print("Calling get_wip_trace...")
    result = get_wip_trace(wip_id="WIP-KR02PSA251101-001", db=db, current_user=admin)
    print(f"Result: {result}")
    
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    db.close()
