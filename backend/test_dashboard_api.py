"""
Test the dashboard API endpoint directly.
"""
import sys
from app.main import app
from fastapi.testclient import TestClient

def test_dashboard():
    client = TestClient(app)
    
    # First, login to get a token
    print("Logging in...")
    response = client.post("/api/v1/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.json())
        return False
    
    token = response.json()["access_token"]
    print(f"✓ Login successful, got token")
    
    # Now test the dashboard endpoint
    print("\nTesting dashboard summary endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/dashboard/summary", headers=headers)
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Dashboard summary successful!")
        print(f"  - Date: {data.get('date')}")
        print(f"  - Total started: {data.get('total_started')}")
        print(f"  - Total completed: {data.get('total_completed')}")
        print(f"  - Total defective: {data.get('total_defective')}")
        print(f"  - Defect rate: {data.get('defect_rate')}%")
        print(f"  - Lots: {len(data.get('lots', []))}")
        print(f"  - Process WIP: {len(data.get('process_wip', []))}")
        return True
    else:
        print(f"✗ Dashboard summary failed!")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    try:
        success = test_dashboard()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
