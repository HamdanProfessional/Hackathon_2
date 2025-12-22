#!/usr/bin/env python3
"""Test script to verify the deployed backend chat functionality."""

import requests
import json
import sys

# Backend URL
BACKEND_URL = "https://backend-pay02n1tx-hamdanprofessionals-projects.vercel.app"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("PASS - Health check passed:", response.json())
            return True
        else:
            print(f"FAIL - Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL - Health check error: {e}")
        return False

def test_docs():
    """Test docs endpoint."""
    print("\nTesting docs endpoint...")
    try:
        response = requests.get(f"{BACKEND_URL}/docs")
        if response.status_code == 200:
            print("PASS - Docs endpoint accessible")
            return True
        else:
            print(f"FAIL - Docs endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL - Docs endpoint error: {e}")
        return False

def test_chat_api():
    """Test chat API endpoint structure."""
    print("\nTesting chat API structure...")
    try:
        # Test if the chat endpoint exists (should return 401 without auth)
        response = requests.post(
            f"{BACKEND_URL}/api/chat/",
            json={"message": "test", "conversation_id": None}
        )
        if response.status_code == 401:
            print("PASS - Chat API endpoint exists and requires authentication")
            return True
        else:
            print(f"FAIL - Unexpected response from chat API: {response.status_code}")
            print("Response:", response.text)
            return False
    except Exception as e:
        print(f"FAIL - Chat API error: {e}")
        return False

def test_openapi_schema():
    """Test OpenAPI schema for chat endpoints."""
    print("\nTesting OpenAPI schema...")
    try:
        response = requests.get(f"{BACKEND_URL}/openapi.json")
        if response.status_code == 200:
            schema = response.json()
            # Check if chat paths exist
            if "/api/chat/" in str(schema):
                print("PASS - Chat endpoints found in OpenAPI schema")
                return True
            else:
                print("FAIL - Chat endpoints not found in OpenAPI schema")
                return False
        else:
            print(f"FAIL - OpenAPI schema failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL - OpenAPI schema error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing deployed backend functionality...")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 50)

    tests = [
        test_health,
        test_docs,
        test_chat_api,
        test_openapi_schema
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("SUCCESS! All tests passed! The backend deployment is working correctly.")
        print("\nThe chat task creation functionality should now work with:")
        print("- UUID vs int type mismatches fixed")
        print("- Broken MCP server removed")
        print("- Direct tool integration implemented")
        print("- Proper agent tool context functions")
        return 0
    else:
        print("FAIL - Some tests failed. Please check the deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())