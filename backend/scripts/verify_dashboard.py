import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

def verify_dashboard():
    print(f"1. Authenticating as {USERNAME}...")
    try:
        # Login
        login_data = urllib.parse.urlencode({
            "username": USERNAME, 
            "password": PASSWORD
        }).encode()
        
        req = urllib.request.Request(
            f"{BASE_URL}/auth/login", 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"❌ Login failed: {response.status}")
                return False
            
            token_data = json.loads(response.read().decode())
            access_token = token_data.get("access_token")
            print("✅ Login successful")
        
        print("\n2. Checking Dashboard Summary...")
        req = urllib.request.Request(
            f"{BASE_URL}/dashboard/summary",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("✅ Dashboard Summary API is working!")
                data = json.loads(response.read().decode())
                print(json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Dashboard API failed: {response.status}")
                return False
            
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        print(e.read().decode())
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_dashboard()
    sys.exit(0 if success else 1)
