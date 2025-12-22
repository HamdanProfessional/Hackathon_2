"""Test chat endpoint directly to see actual error"""
import requests
import json

# First, register/login to get a token
BASE_URL = "https://backend-jauhld2ii-hamdanprofessionals-projects.vercel.app"

# Try to register a test user
register_data = {
    "email": "testchat@test.com",
    "password": "testpass123",
    "name": "Test User"
}

print("Attempting to register/login...")
try:
    register_response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Register status: {register_response.status_code}")
except Exception as e:
    print(f"Register failed, trying login: {e}")

# Try login
login_data = {
    "email": "testchat@test.com",
    "password": "testpass123"
}

login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
print(f"Login status: {login_response.status_code}")
print(f"Login response: {login_response.json()}")

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print(f"\nGot token: {token[:20]}...")

    # Now test chat endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    chat_data = {
        "message": "Hello, create a test task"
    }

    print(f"\nSending chat request...")
    chat_response = requests.post(f"{BASE_URL}/api/chat", json=chat_data, headers=headers)
    print(f"Chat status: {chat_response.status_code}")
    print(f"Chat response: {json.dumps(chat_response.json(), indent=2)}")
else:
    print("Failed to get token")
