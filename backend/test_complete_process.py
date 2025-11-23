"""
Test script to reproduce the complete process 500 error
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login first
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login/json",
    json={"username": "admin", "password": "admin"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Login successful\n")

# Try to complete a process
print("2. Testing process complete...")
print("=" * 60)

# Typical payload from PySide app
test_payloads = [
    # Minimal payload
    {
        "lot_number": "WIP-KR02PSA251101-003",
        "process_id": 1,
        "result": "PASS"
    },
    # With measurement data
    {
        "lot_number": "WIP-KR02PSA251101-003",
        "process_id": 1,
        "result": "PASS",
        "measurement_data": {}
    },
]

for i, payload in enumerate(test_payloads, 1):
    print(f"\nTest {i}: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/process-operations/complete",
        headers=headers,
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Success: {response.json()}")
        break
    else:
        print(f"❌ Error: {response.text[:500]}")
        
        # Try to get more details from error response
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass

print("\n" + "=" * 60)
