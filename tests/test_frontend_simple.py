"""Simple test for frontend using requests"""
import requests
import json
from urllib.parse import urljoin

def test_frontend():
    print("=" * 70)
    print("TESTING FRONTEND")
    print("=" * 70)

    FRONTEND_URL = "https://frontend-gmdr4s6rk-hamdanprofessionals-projects.vercel.app"
    BACKEND_URL = "https://backend-k4t2o36f2-hamdanprofessionals-projects.vercel.app"

    print(f"\nFrontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print("-" * 70)

    # Test 1: Check frontend accessibility
    print("\n1. Testing frontend page load...")
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   [OK] Frontend loads successfully")

            # Check for common elements
            if "chat" in response.text.lower():
                print("   ✓ Chat-related content found")
            if "login" in response.text.lower():
                print("   ✓ Login-related content found")

            # Check for API URL in the page
            if BACKEND_URL in response.text or "backend-" in response.text:
                print("   ✓ Backend URL appears to be configured")
            else:
                print("   ⚠ Backend URL not found in page source")

        else:
            print(f"   ✗ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Frontend unreachable: {e}")

    # Test 2: Test backend health
    print("\n2. Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Backend is reachable")
            data = response.json()
            print(f"   Version: {data.get('version', 'N/A')}")
        else:
            print(f"   ✗ Backend error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Backend unreachable: {e}")

    # Test 3: Test authentication flow
    print("\n3. Testing authentication...")
    try:
        # Login
        login_response = requests.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"email": "test1@test.com", "password": "Test1234"},
            timeout=10
        )
        print(f"   Login status: {login_response.status_code}")

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print("   ✓ Login successful")

            # Test chat endpoint
            print("\n4. Testing chat endpoint...")
            chat_response = requests.post(
                f"{BACKEND_URL}/api/chat",
                json={"message": "Hello from test"},
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            print(f"   Chat status: {chat_response.status_code}")

            if chat_response.status_code == 200:
                response_data = chat_response.json()
                ai_response = response_data.get("response", "")
                if ai_response:
                    print(f"   ✓ AI response: {ai_response[:100]}...")
                else:
                    print("   ⚠ Empty AI response")
            else:
                print(f"   ✗ Chat error: {chat_response.text}")

            # Test conversations endpoint
            print("\n5. Testing conversations endpoint...")
            conv_response = requests.get(
                f"{BACKEND_URL}/api/chat/conversations",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            print(f"   Conversations status: {conv_response.status_code}")

            if conv_response.status_code == 200:
                conv_data = conv_response.json()
                if isinstance(conv_data, list):
                    print(f"   ✓ Found {len(conv_data)} conversations")
                elif isinstance(conv_data, dict) and "conversations" in conv_data:
                    print(f"   ✓ Found {len(conv_data['conversations'])} conversations")

        else:
            print(f"   ✗ Login failed: {login_response.text}")

    except Exception as e:
        print(f"   ✗ Authentication error: {e}")

    # Test 4: Check CORS configuration
    print("\n6. Testing CORS...")
    try:
        options_response = requests.options(
            f"{BACKEND_URL}/api/auth/login",
            headers={"Origin": FRONTEND_URL},
            timeout=10
        )

        cors_headers = {
            'Access-Control-Allow-Origin': options_response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': options_response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': options_response.headers.get('Access-Control-Allow-Headers')
        }

        print("   CORS Headers:")
        for key, value in cors_headers.items():
            if value:
                print(f"   ✓ {key}: {value}")
            else:
                print(f"   ⚠ {key}: Not set")

    except Exception as e:
        print(f"   CORS check failed: {e}")

    # Test 5: Check frontend's Next.js build
    print("\n7. Testing Next.js build info...")
    try:
        # Check for build manifest
        build_response = requests.get(f"{FRONTEND_URL}/_next/static/chunks/pages/_app.js", timeout=10)
        if build_response.status_code == 200:
            print("   ✓ Next.js build assets accessible")
        else:
            print("   ⚠ Next.js build assets not accessible (404 is normal for SSR)")
    except Exception as e:
        print(f"   Build check failed: {e}")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("\nIf tests pass but the app still doesn't work in browser:")
    print("1. Check browser console for JavaScript errors")
    print("2. Verify API_URL is correctly set in Next.js config")
    print("3. Clear browser cache and cookies")
    print("4. Try incognito/private browsing mode")

if __name__ == "__main__":
    test_frontend()
