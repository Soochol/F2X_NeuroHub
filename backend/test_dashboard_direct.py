"""
Test dashboard endpoint directly with proper imports.
"""
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app.models import User
from app.api.v1.dashboard import get_dashboard_summary

def test_dashboard():
    db = SessionLocal()
    try:
        # Get admin user
        user = db.query(User).filter(User.username == 'admin').first()
        if not user:
            print("Admin user not found!")
            return False
        
        print(f"Testing dashboard endpoint with user: {user.username}")
        
        # Call the dashboard endpoint with target_date=None (will use today)
        result = get_dashboard_summary(db=db, target_date=None, current_user=user)
        
        print("✓ Dashboard endpoint successful!")
        print(f"  - Date: {result['date']}")
        print(f"  - Total started: {result['total_started']}")
        print(f"  - Total completed: {result['total_completed']}")
        print(f"  - Lots: {len(result['lots'])}")
        print(f"  - Process WIP: {len(result['process_wip'])}")
        
        return True
    except Exception as e:
        print(f"✗ Dashboard endpoint failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = test_dashboard()
    sys.exit(0 if success else 1)
