
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_history():
    username = "test_farmer_2"
    password = "password123"
    
    # 1. Register/Login
    print(f"Logging in user: {username}...")
    headers = {}
    
    # Try login first
    login_payload = {"username": username, "password": password}
    resp = requests.post(f"{BASE_URL}/login", json=login_payload)
    
    if resp.status_code == 401:
        # Register if login fails
        print("Registering...")
        requests.post(f"{BASE_URL}/register", json=login_payload)
        resp = requests.post(f"{BASE_URL}/login", json=login_payload)
        
    if resp.status_code == 200:
        token = resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"}
        print("Login Successful!")
    else:
        print("Login Failed")
        sys.exit(1)
        
    # 2. Make a Recommendation (Save to DB)
    print("Requesting recommendation...")
    rec_payload = {"location": "Bengaluru"}
    resp = requests.post(f"{BASE_URL}/recommend", json=rec_payload, headers=headers)
    if resp.status_code == 200:
        print("Recommendation received and saved!")
    else:
        print(f"Recommendation Failed: {resp.text}")
        sys.exit(1)
        
    # 3. Fetch History
    print("Fetching History...")
    resp = requests.get(f"{BASE_URL}/history", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"History items found: {len(data)}")
        if len(data) > 0:
            print("Latest Item:", data[0])
    else:
        print(f"History Fetch Failed: {resp.text}")

if __name__ == "__main__":
    test_history()
