#!/usr/bin/env python3
"""
Debug MCP Tool Invocation Issue

This script tests if MCP tools are being called by the AI agent.
"""

import requests
import json

# Production backend URL
BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

# Test credentials (use timestamp for unique email)
import time
TEST_EMAIL = f"debug{int(time.time())}@example.com"
TEST_PASSWORD = "DebugPass123!"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print("""
====================================================
  Phase 3 MCP Tool Debug Test
====================================================""")

    # Step 1: Register/Login
    print_section("1. Authentication")

    response = requests.post(f"{BACKEND_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Debug User"
    })

    if response.status_code not in [200, 201]:
        # Try login instead
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })

    # Accept 200 or 201 for auth
    if response.status_code not in [200, 201]:
        print(f"[FAIL] Authentication failed: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    token = data.get("access_token")
    print(f"[OK] Authenticated with token: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Test chat with explicit task creation request
    print_section("2. Testing Chat: 'Create a task to buy milk'")

    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": "Create a task to buy milk"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"[FAIL] Chat request failed")
        print(response.text)
        return

    data = response.json()
    print(f"\n--- FULL RESPONSE ---")
    print(json.dumps(data, indent=2))
    print(f"\n--- END RESPONSE ---")

    # Analyze response
    print_section("3. Analysis")

    response_text = data.get("response", "")
    tool_calls = data.get("tool_calls", [])

    print(f"AI Response: {response_text[:200]}...")
    print(f"Tool Calls: {tool_calls}")
    print(f"Number of tool calls: {len(tool_calls)}")

    # Check each tool call
    if tool_calls:
        for i, tc in enumerate(tool_calls):
            print(f"\n  Tool Call {i+1}:")
            if tc:
                print(f"    Type: {type(tc)}")
                print(f"    Keys: {tc.keys() if isinstance(tc, dict) else 'N/A'}")
                if isinstance(tc, dict):
                    print(f"    Content: {tc}")
            else:
                print(f"    Value: {tc}")

    # Check if tools were actually called
    print_section("4. Verification")

    # Direct API check: Get tasks
    response = requests.get(f"{BACKEND_URL}/api/tasks", headers=headers)
    if response.status_code == 200:
        tasks = response.json()
        print(f"Total tasks in database: {len(tasks)}")
        for task in tasks:
            print(f"  - {task.get('title')} (completed: {task.get('completed')})")

        # Check if task was created
        if any("milk" in t.get("title", "").lower() for t in tasks):
            print("\n[OK] Task 'buy milk' WAS created in database!")
        else:
            print("\n[FAIL] Task 'buy milk' was NOT found in database")
    else:
        print(f"[FAIL] Could not fetch tasks: {response.status_code}")

    # Test 2: List tasks request
    print_section("5. Testing Chat: 'Show me all my tasks'")

    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={
            "message": "Show me all my tasks",
            "conversation_id": data.get("conversation_id")
        }
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"AI Response: {data.get('response', '')[:200]}...")
        print(f"Tool Calls: {data.get('tool_calls', [])}")

        # Check if list_tasks tool was called
        tool_calls = data.get("tool_calls", [])
        if tool_calls and any(tc.get("name") == "list_tasks" for tc in tool_calls if tc):
            print("\n[OK] list_tasks tool WAS called!")
        else:
            print("\n[FAIL] list_tasks tool was NOT called")

if __name__ == "__main__":
    main()
