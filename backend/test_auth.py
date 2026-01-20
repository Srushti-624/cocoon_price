
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_auth():
    username = "test_farmer_1"
    password = "secure_password_123"
    
    # 1. Register
    print(f"Registering user: {username}...")
    reg_payload = {"username": username, "password": password}
    try:
        resp = requests.post(f"{BASE_URL}/register", json=reg_payload)
        if resp.status_code == 201:
            print("Registration Successful!")
        elif resp.status_code == 400 and "already exists" in resp.text:
            print("User already exists, continuing to login...")
        else:
            print(f"Registration Failed: {resp.status_code} - {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Registration Error: {e}")
        sys.exit(1)
        
    # 2. Login
    print(f"Logging in user: {username}...")
    login_payload = {"username": username, "password": password}
    try:
        resp = requests.post(f"{BASE_URL}/login", json=login_payload)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            if token:
                print("Login Successful!")
                print(f"Token received: {token[:20]}...")
            else:
                print("Login Failed: No token returned.")
                sys.exit(1)
        else:
            print(f"Login Failed: {resp.status_code} - {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"Login Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_auth()
