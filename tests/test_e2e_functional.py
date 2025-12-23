#!/usr/bin/env python3
"""
End-to-End Functional Test for Phase 3 AI Chatbot
Tests actual functionality: auth, chat, MCP tools, task CRUD, conversations
"""

import requests
import json
import time
from typing import Optional, Dict, Any

# Production backend URL (Vercel)
BASE_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

# Unique test user
TIMESTAMP = int(time.time())
TEST_EMAIL = f"e2etest{TIMESTAMP}@example.com"
TEST_PASSWORD = "TestPassword123!"

def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"      {details}")

# Track results
results = []

def test_register():
    """Test user registration."""
    print_section("1. User Registration")

    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "E2E Test User"
    }

    response = requests.post(f"{BASE_URL}/api/auth/register", json=payload)

    passed = response.status_code in [200, 201]
    details = f"Status: {response.status_code}"

    if passed:
        data = response.json()
        if "access_token" in data:
            details += f" | Token received: {data['access_token'][:20]}..."
            return data["access_token"]
        else:
            passed = False
            details += " | No token in response"

    print_result("User Registration", passed, details)
    results.append(("Registration", passed))
    return None

def test_login() -> Optional[str]:
    """Test user login."""
    print_section("2. User Login")

    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }

    response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)

    passed = response.status_code == 200
    details = f"Status: {response.status_code}"

    if passed:
        data = response.json()
        if "access_token" in data:
            details += f" | Token: {data['access_token'][:20]}..."
            print_result("User Login", True, details)
            results.append(("Login", True))
            return data["access_token"]

    print_result("User Login", False, details)
    results.append(("Login", False))
    return None

def test_chat_with_mcp_tools(token: str) -> Dict[str, Any]:
    """Test AI chat that triggers MCP tools."""
    print_section("3. AI Chat with MCP Tools")

    headers = {"Authorization": f"Bearer {token}"}

    # Test 1: Create a task via chat
    print("\n  Test 3.1: Create task via chat...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={"message": "Create a task to buy groceries"}
    )

    data = response.json()
    conversation_id = data.get("conversation_id")

    tool_calls = data.get("tool_calls", [])
    ai_response = data.get("response", "")

    has_create_tool = any(tc.get("function") == "create_task" for tc in tool_calls)
    print_result("Chat: Create Task Tool Called", has_create_tool,
                f"Tools: {[tc.get('function') for tc in tool_calls]}")

    results.append(("Create Task MCP", has_create_tool))

    # Test 2: List tasks via chat
    print("\n  Test 3.2: List tasks via chat...")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={
            "message": "Show me all my tasks",
            "conversation_id": conversation_id
        }
    )

    data = response.json()
    tool_calls = data.get("tool_calls", [])
    has_list_tool = any(tc.get("function") == "get_tasks" for tc in tool_calls)
    print_result("Chat: Get Tasks Tool Called", has_list_tool,
                f"Tools: {[tc.get('function') for tc in tool_calls]}")

    results.append(("Get Tasks MCP", has_list_tool))

    return {"conversation_id": conversation_id}

def test_task_crud(token: str) -> bool:
    """Test direct Task CRUD operations."""
    print_section("4. Task CRUD Operations")

    headers = {"Authorization": f"Bearer {token}"}

    # Test 4.1: Create task directly
    print("\n  Test 4.1: Create task via API...")
    response = requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json={
            "title": "E2E Test Task",
            "description": "Created by E2E test",
            "priority": "high"
        }
    )

    created = response.status_code == 201
    task_id = None
    if created:
        task = response.json()
        task_id = task.get("id")
        print_result("Create Task API", True, f"Task ID: {task_id}, Title: {task.get('title')}")
    else:
        print_result("Create Task API", False, f"Status: {response.status_code}")
    results.append(("Create Task API", created))

    if not task_id:
        return False

    # Test 4.2: Get all tasks
    print("\n  Test 4.2: Get all tasks...")
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    tasks = response.json()
    found_task = any(t.get("id") == task_id for t in tasks)
    print_result("Get Tasks API", found_task, f"Found {len(tasks)} tasks")
    results.append(("Get Tasks API", found_task))

    # Test 4.3: Update task
    print("\n  Test 4.3: Update task...")
    response = requests.put(
        f"{BASE_URL}/api/tasks/{task_id}",
        headers=headers,
        json={"completed": True}
    )
    updated = response.status_code == 200
    if updated:
        task = response.json()
        print_result("Update Task API", task.get("completed") == True, "Task marked complete")
    else:
        print_result("Update Task API", False, f"Status: {response.status_code}")
    results.append(("Update Task API", updated))

    # Test 4.4: Delete task
    print("\n  Test 4.4: Delete task...")
    response = requests.delete(f"{BASE_URL}/api/tasks/{task_id}", headers=headers)
    deleted = response.status_code in [200, 204]
    print_result("Delete Task API", deleted, f"Status: {response.status_code}")
    results.append(("Delete Task API", deleted))

    return created and found_task and updated and deleted

def test_all_mcp_tools(token: str) -> bool:
    """Test all 5 MCP tools are accessible."""
    print_section("5. Verify All 5 MCP Tools")

    headers = {"Authorization": f"Bearer {token}"}

    # Create a test task first
    requests.post(
        f"{BASE_URL}/api/tasks",
        headers=headers,
        json={"title": "MCP Test Task", "priority": "medium"}
    )

    all_passed = True

    # Test each MCP tool via chat
    mcp_tests = [
        ("get_tasks", "Show me all my tasks"),
        ("create_task", "Create a new task to test MCP"),
        ("update_task", "Mark the first task as completed"),
        ("delete_task", "Delete the test task"),
        ("get_task", "Show me details of task 1"),
    ]

    for tool_name, message in mcp_tests:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers=headers,
            json={"message": message}
        )
        data = response.json()
        tool_calls = data.get("tool_calls", [])
        found = any(tc.get("function") == tool_name for tc in tool_calls)
        print_result(f"MCP Tool: {tool_name}", found, f"Message: {message}")
        results.append((f"MCP {tool_name}", found))
        if not found:
            all_passed = False

    return all_passed

def test_conversation_persistence(token: str) -> bool:
    """Test conversation history persistence."""
    print_section("6. Conversation Persistence")

    headers = {"Authorization": f"Bearer {token}"}

    # Get conversations
    response = requests.get(f"{BASE_URL}/api/chat/conversations", headers=headers)
    conversations = response.json()

    has_conversations = len(conversations) > 0
    print_result("Conversations Exist", has_conversations, f"Found {len(conversations)} conversation(s)")

    if has_conversations:
        conv_id = conversations[0].get("id")

        # Get conversation details
        response = requests.get(
            f"{BASE_URL}/api/chat/conversations/{conv_id}",
            headers=headers
        )
        details = response.status_code == 200
        if details:
            conv = response.json()
            message_count = len(conv.get("messages", []))
            print_result("Conversation Details", True, f"Messages: {message_count}")
        else:
            print_result("Conversation Details", False, f"Status: {response.status_code}")

        results.append(("Conversation Details", details))
        return details

    results.append(("Conversation Details", False))
    return False

def test_ai_agent_intelligence(token: str) -> bool:
    """Test AI agent can intelligently use tools."""
    print_section("7. AI Agent Intelligence")

    headers = {"Authorization": f"Bearer {token}"}

    # Test complex query that requires tool chaining
    print("\n  Test: Complex query - 'What high priority tasks do I have?'")
    response = requests.post(
        f"{BASE_URL}/api/chat",
        headers=headers,
        json={"message": "What high priority tasks do I have?"}
    )

    data = response.json()
    tool_calls = data.get("tool_calls", [])

    # Should call get_tasks with filter
    has_get_tasks = any(tc.get("function") == "get_tasks" for tc in tool_calls)
    has_response = len(data.get("response", "")) > 0

    print_result("AI Uses Get Tasks", has_get_tasks, "Tool: get_tasks")
    print_result("AI Provides Response", has_response, f"Response length: {len(data.get('response', ''))}")

    results.append(("AI Intelligence", has_get_tasks and has_response))

    return has_get_tasks and has_response

def print_summary():
    """Print test summary."""
    print_section("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {total - passed}")
    print(f"  Success Rate: {passed/total*100:.1f}%")

    print("\n  Detailed Results:")
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"    {status} {name}")

    if passed == total:
        print("\n  *** ALL TESTS PASSED ***")
    else:
        print(f"\n  *** {total - passed} TEST(S) FAILED ***")

    print("\n" + "=" * 60)

def main():
    """Run all E2E tests."""
    print("""
====================================================
  Phase 3 AI Chatbot - E2E Functional Test Suite
  Testing: Production (Vercel)
====================================================
    """)

    # Test 1 & 2: Auth
    token = test_register()
    if not token:
        token = test_login()

    if not token:
        print("\n[FATAL] Could not authenticate. Exiting.")
        return

    # Test 3: Chat with MCP
    chat_info = test_chat_with_mcp_tools(token)

    # Test 4: Task CRUD
    test_task_crud(token)

    # Test 5: All MCP tools
    test_all_mcp_tools(token)

    # Test 6: Conversation persistence
    test_conversation_persistence(token)

    # Test 7: AI intelligence
    test_ai_agent_intelligence(token)

    # Summary
    print_summary()

if __name__ == "__main__":
    main()
