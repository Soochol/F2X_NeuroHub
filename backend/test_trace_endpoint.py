import requests
import json

# Get token
auth_response = requests.post(
    "http://localhost:8000/api/v1/auth/login/json",
    json={"username": "admin", "password": "admin"}
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.text}")
    exit(1)

token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test the trace endpoint
wip_id = "WIP-KR02PSA251101-003"
url = f"http://localhost:8000/api/v1/wip-items/{wip_id}/trace"

print(f"Testing URL: {url}")
print(f"Headers: {headers}")

try:
    response = requests.get(url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
    print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
