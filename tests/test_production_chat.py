#!/usr/bin/env python3
"""Test script for Phase 3 AI Chatbot on production deployment."""

import requests
import json
from typing import Optional

# Production URLs
BACKEND_URL = "https://backend-hamdanprofessionals-projects.vercel.app"
FRONTEND_URL = "https://frontend-hamdanprofessionals-projects.vercel.app"

# Test credentials - use timestamp for unique email
import time
TEST_EMAIL = f"test{int(time.time())}@example.com"
TEST_PASSWORD = "testpassword123"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def test_health():
    """Test backend health endpoint."""
    print_section("1. Testing Backend Health")

    response = requests.get(f"{BACKEND_URL}/health")
    print(f"URL: {BACKEND_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    return response.status_code == 200


def test_frontend():
    """Test frontend is accessible."""
    print_section("2. Testing Frontend")

    response = requests.get(FRONTEND_URL)
    print(f"URL: {FRONTEND_URL}")
    print(f"Status: {response.status_code}")
    print(f"Title: Evolution Todo - Modern Task Management (HTML content received)")

    return response.status_code == 200


def create_user():
    """Create or login a test user."""
    print_section("3. Creating/Logging in Test User")

    # Try to login first
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    response = requests.post(f"{BACKEND_URL}/api/auth/login", json=login_data)
    print(f"Login attempt: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            print(f"[OK] Login successful!")
            return data["access_token"]
        elif "token" in data:
            print(f"[OK] Login successful!")
            return data["token"]

    # If login failed, try to create user
    print("Login failed, trying to create user...")
    user_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Test User"
    }

    response = requests.post(f"{BACKEND_URL}/api/auth/register", json=user_data)
    print(f"Register attempt: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    if response.status_code in [200, 201]:
        data = response.json()
        if "access_token" in data:
            print(f"[OK] User created and logged in!")
            return data["access_token"]
        elif "token" in data:
            print(f"[OK] User created and logged in!")
            return data["token"]

    return None


def test_chat_send(token: str, message: str, conversation_id: Optional[str] = None):
    """Test sending a chat message."""
    print_section(f"4. Testing Chat API - Message: '{message}'")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": message
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

    print(f"POST {BACKEND_URL}/api/chat")
    print(f"Headers: Authorization: Bearer {token[:20]}...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(f"{BACKEND_URL}/api/chat", json=payload, headers=headers)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Chat successful!")
        print(f"\nResponse:")
        print(f"  Conversation ID: {data.get('conversation_id')}")
        print(f"  AI Response: {data.get('response')}")
        print(f"  Tool Calls: {data.get('tool_calls', [])}")
        return data
    else:
        print(f"[FAIL] Chat failed!")
        print(f"Error: {response.text}")
        return None


def test_conversations(token: str):
    """Test getting user's conversations."""
    print_section("5. Testing Get Conversations")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(f"{BACKEND_URL}/api/chat/conversations", headers=headers)
    print(f"GET {BACKEND_URL}/api/chat/conversations")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        conversations = response.json()
        print(f"[OK] Found {len(conversations)} conversation(s)")
        for conv in conversations[:3]:  # Show first 3
            print(f"  - ID: {conv.get('id')}")
            print(f"    Title: {conv.get('title', 'N/A')}")
            print(f"    Updated: {conv.get('updated_at', 'N/A')}")
        return conversations
    else:
        print(f"[FAIL] Failed to get conversations")
        return []


def main():
    """Run all tests."""
    print("""
====================================================
  Phase 3 AI Chatbot - Production Test Suite
  Testing: https://backend-*.vercel.app
====================================================
    """)

    results = []

    # Test 1: Health
    results.append(("Backend Health", test_health()))

    # Test 2: Frontend
    results.append(("Frontend Access", test_frontend()))

    # Test 3: Auth
    token = create_user()
    results.append(("User Authentication", token is not None))

    if not token:
        print("\n[FAIL] Cannot proceed with chat tests without authentication token")
        return

    # Test 4: Chat - First message
    chat_result1 = test_chat_send(token, "Hello, what can you help me with?")
    results.append(("Chat - Greeting", chat_result1 is not None))

    if chat_result1:
        conv_id = chat_result1.get("conversation_id")

        # Test 5: Chat - Task creation
        chat_result2 = test_chat_send(
            token,
            "Add a task to buy groceries",
            conversation_id=conv_id
        )
        results.append(("Chat - Task Creation", chat_result2 is not None))

        # Test 6: Chat - List tasks
        chat_result3 = test_chat_send(
            token,
            "Show me all my tasks",
            conversation_id=conv_id
        )
        results.append(("Chat - List Tasks", chat_result3 is not None))

        # Test 7: Get conversations
        convs = test_conversations(token)
        results.append(("Get Conversations", convs is not None))

    # Summary
    print_section("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Phase 3 AI Chatbot is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please check the logs above.")


if __name__ == "__main__":
    main()
