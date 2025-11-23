import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Without authentication
print("Test 1: Without authentication")
response = requests.get(f"{BASE_URL}/wip-items/WIP-KR02PSA251101-001/trace")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

# 2. With authentication
print("\nTest 2: With authentication")
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "password123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/wip-items/WIP-KR02PSA251101-001/trace", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
else:
    print(f"Login failed: {login_response.text}")
