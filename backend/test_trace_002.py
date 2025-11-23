import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin",
    "password": "password123"
})

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test with WIP-002
    print("Testing with WIP-KR02PSA251101-002")
    response = requests.get(f"{BASE_URL}/wip-items/WIP-KR02PSA251101-002/trace", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        import json
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text[:500]}")
else:
    print(f"Login failed: {login_response.text}")
