#!/usr/bin/env python3
"""Test which AI service is being used and API key validation."""

import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.ai.agent import AgentService
from app.ai.agent_mock import MockAgentService


def test_service_configuration():
    """Test which AI service would be used based on configuration."""

    print("AI Service Configuration Test")
    print("=" * 50)

    print(f"AI_API_KEY from config: '{settings.AI_API_KEY}'")
    print(f"AI_BASE_URL: {settings.AI_BASE_URL}")
    print(f"AI_MODEL: {settings.AI_MODEL}")

    # Check if the key looks valid
    api_key = settings.AI_API_KEY
    if not api_key or not api_key.strip():
        print("\n[ERROR] AI_API_KEY is empty or not set")
        print("   -> System will use MockAgentService")
        return "mock"
    elif api_key.startswith("AIzaSy") and len(api_key) > 35:
        print(f"\n[OK] AI_API_KEY appears to be a valid Google Gemini key")
        print(f"   -> System should use AgentService")
        return "real"
    else:
        print(f"\n[WARNING] AI_API_KEY might be invalid:")
        print(f"      Length: {len(api_key)}")
        print(f"      Starts with: {api_key[:10]}...")
        print("   -> System might fall back to MockAgentService")
        return "uncertain"

    # Test which service would be chosen
    use_mock_ai = not bool(settings.AI_API_KEY and settings.AI_API_KEY.strip())
    print(f"\nUSE_MOCK_AI calculation: {use_mock_ai}")

    if use_mock_ai:
        print("-> MockAgentService would be used")
        return "mock"
    else:
        print("-> AgentService would be used")
        return "real"


def test_direct_api_call():
    """Test if we can make a direct call to the Gemini API."""

    print("\n" + "=" * 50)
    print("Direct API Call Test")
    print("=" * 50)

    try:
        import httpx
        import json

        # Try to call the models endpoint to see if API key works
        url = f"{settings.AI_BASE_URL}models"
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json"
        }

        print(f"Testing API endpoint: {url}")
        print(f"Using key: {settings.AI_API_KEY[:10]}...")

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("[OK] API key is valid and working")
            data = response.json()
            print(f"Available models: {len(data.get('data', []))} models found")
            return True
        else:
            print(f"[ERROR] API call failed")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response body: {response.text}")
            return False

    except Exception as e:
        print(f"[ERROR] Exception during API test: {type(e).__name__}: {e}")
        return False


def test_mock_service_behavior():
    """Test what the mock service returns for different operations."""

    print("\n" + "=" * 50)
    print("Mock Service Behavior Test")
    print("=" * 50)

    # This would show what happens when the mock service is used
    # Since we can't easily test the async flow here, we'll just show the logic

    print("MockAgentService behavior:")
    print("- Uses pattern matching to understand user requests")
    print("- Calls the actual tool functions (add_task, list_tasks, etc.)")
    print("- Should work the same as real service for basic operations")
    print("- Only difference is in AI understanding of natural language")

    print("\nIf user says 'delete task', mock service:")
    print("1. Calls list_tasks to get user's tasks")
    print("2. Tries to match task by name/pattern")
    print("3. Calls delete_task with the found task_id")
    print("4. Returns success/failure message to user")


if __name__ == "__main__":
    service_type = test_service_configuration()
    api_works = test_direct_api_call()
    test_mock_service_behavior()

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Service type detected: {service_type}")
    print(f"Direct API call works: {api_works}")

    if service_type == "mock" or not api_works:
        print("\n[RECOMMENDATION]:")
        print("The system is likely using MockAgentService.")
        print("This should still work for task operations, but the AI understanding")
        print("might be limited to basic patterns.")
    else:
        print("\n[OK] System should be using real AgentService with Gemini AI")

    print("\n[NEXT STEPS]:")
    print("1. Check if the user is getting specific error messages")
    print("2. Verify the frontend is properly calling the chat endpoint")
    print("3. Check if there are CORS or authentication issues")
    print("4. Look at the actual error logs from the running application")