#!/usr/bin/env python3
"""
Test MCP tools with provided credentials
Email: testex@test.com
Password: test1234
"""

import requests
import json

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

TEST_EMAIL = "testex@test.com"
TEST_PASSWORD = "test1234"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print("""
====================================================
  MCP Tools Test with Provided Credentials
====================================================""")

    # Step 1: Login
    print_section("1. Login")

    response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })

    print(f"Status: {response.status_code}")

    if response.status_code not in [200, 201]:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    token = data.get("access_token")
    print(f"[OK] Logged in with token: {token[:20]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Test direct API - List tasks
    print_section("2. Test Direct API - List Tasks")

    response = requests.get(f"{BACKEND_URL}/api/tasks", headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        tasks = response.json()
        print(f"[OK] Got {len(tasks)} tasks")
        for task in tasks[:3]:
            print(f"  - {task.get('title')} (completed: {task.get('completed')})")
    else:
        print(f"[FAIL] {response.text}")

    # Step 3: Test Chat - List tasks via AI
    print_section("3. Test Chat - 'Show me all my tasks'")

    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": "Show me all my tasks"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"[FAIL] Chat failed: {response.text}")
        return

    data = response.json()
    print(f"\n--- AI Response ---")
    print(data.get("response", "")[:500])
    print(f"\n--- Tool Calls ---")
    tool_calls = data.get("tool_calls", [])
    print(f"Number of tool calls: {len(tool_calls)}")
    for i, tc in enumerate(tool_calls):
        if tc:
            print(f"  Tool {i+1}: {tc}")

    # Step 4: Test Chat - Create a task via AI
    print_section("4. Test Chat - 'Create a task to test MCP'")

    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": "Create a task to test MCP functionality"}
    )

    print(f"Status: {response.status_code}")

    if response.status_code != 200:
        print(f"[FAIL] Chat failed: {response.text}")
        return

    data = response.json()
    print(f"\n--- AI Response ---")
    print(data.get("response", "")[:500])
    print(f"\n--- Tool Calls ---")
    tool_calls = data.get("tool_calls", [])
    print(f"Number of tool calls: {len(tool_calls)}")
    for i, tc in enumerate(tool_calls):
        if tc:
            print(f"  Tool {i+1}: {tc}")

    # Step 5: Verify task was created
    print_section("5. Verify Task Created")

    response = requests.get(f"{BACKEND_URL}/api/tasks", headers=headers)
    if response.status_code == 200:
        tasks = response.json()
        test_tasks = [t for t in tasks if "MCP" in t.get("title", "")]
        if test_tasks:
            print(f"[OK] Found {len(test_tasks)} MCP test task(s)")
            for task in test_tasks:
                print(f"  - {task.get('title')}")
        else:
            print(f"[FAIL] No MCP test task found")

    # Step 6: Check OpenAI/AI provider configuration
    print_section("6. AI Provider Check")

    # Check if tools were actually called
    if tool_calls:
        print("[OK] MCP tools ARE being called by the AI agent")
        print("\nTool details:")
        for tc in tool_calls:
            if tc:
                print(f"  - Name: {tc.get('name')}")
                print(f"    Arguments: {tc.get('arguments')}")
    else:
        print("[FAIL] No MCP tools were called!")
        print("\nPossible issues:")
        print("  1. AI provider (Groq) not configured correctly")
        print("  2. Tool definitions not being sent to AI")
        print("  3. AI refusing to use tools (safety/policy)")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
