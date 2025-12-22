"""Test production chat endpoint to verify database migration is needed"""
import requests
import json

# Production URLs
BACKEND_URL = "https://backend-kvm8wghw0-hamdanprofessionals-projects.vercel.app"
LOGIN_URL = f"{BACKEND_URL}/api/auth/login"
CHAT_URL = f"{BACKEND_URL}/api/chat"

# Test credentials
EMAIL = "test1@test.com"
PASSWORD = "Test1234"

def test_production_chat():
    print("🔍 Testing Production Chat API...")
    print(f"Backend: {BACKEND_URL}")
    print(f"User: {EMAIL}\n")

    # Step 1: Login
    print("1️⃣ Logging in...")
    try:
        login_response = requests.post(
            LOGIN_URL,
            json={"email": EMAIL, "password": PASSWORD},
            headers={"Content-Type": "application/json"}
        )

        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            return False

        token = login_response.json().get("access_token")
        print(f"✅ Login successful, token received\n")

    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

    # Step 2: Send chat message
    print("2️⃣ Sending test chat message...")
    try:
        chat_response = requests.post(
            CHAT_URL,
            json={"message": "hey"},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        print(f"Status Code: {chat_response.status_code}")

        if chat_response.status_code == 500:
            print("❌ Chat failed with 500 error")
            print(f"Response: {chat_response.json()}\n")
            print("🔧 This confirms the database migration is still needed!")
            print("\n📋 Next step: Run the database migration on production")
            print("   See PRODUCTION_MIGRATION_GUIDE.md for instructions")
            return False

        elif chat_response.status_code == 200:
            print("✅ Chat working successfully!")
            print(f"Response: {json.dumps(chat_response.json(), indent=2)}")
            return True

        else:
            print(f"⚠️ Unexpected status code: {chat_response.status_code}")
            print(f"Response: {chat_response.text}")
            return False

    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

if __name__ == "__main__":
    test_production_chat()
