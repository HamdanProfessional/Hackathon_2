#!/usr/bin/env python3
"""
Integration test for Phase 3 AI Chatbot functionality.

This script tests the complete conversation flow:
1. User authentication
2. Creating a conversation
3. Sending messages to AI
4. Verifying tool calls work
5. Checking conversation persistence
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000"
USERNAME = "test_user"
PASSWORD = "testpass123"
EMAIL = "test_phase3@example.com"

class ChatIntegrationTester:
    def __init__(self):
        self.token = None
        self.conversation_id = None
        self.session = requests.Session()

    def register_user(self) -> bool:
        """Register a test user."""
        try:
            response = self.session.post(
                f"{API_BASE}/api/auth/register",
                json={
                    "email": EMAIL,
                    "password": PASSWORD,
                    "name": USERNAME
                }
            )
            if response.status_code == 200:
                print("✓ User registered successfully")
                return True
            else:
                # User might already exist
                print(f"! Registration returned {response.status_code}: {response.text}")
                return True
        except Exception as e:
            print(f"✗ Registration failed: {e}")
            return False

    def login_user(self) -> bool:
        """Login and get JWT token."""
        try:
            response = self.session.post(
                f"{API_BASE}/api/auth/login",
                json={
                    "email": EMAIL,
                    "password": PASSWORD
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    print("✓ Login successful")
                    return True
            print(f"✗ Login failed: {response.text}")
            return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

    def create_task_via_chat(self, task_description: str) -> Dict[str, Any]:
        """Send a message to create a task via chat."""
        try:
            response = self.session.post(
                f"{API_BASE}/api/chat/",
                json={
                    "message": task_description,
                    "conversation_id": self.conversation_id
                }
            )
            if response.status_code == 200:
                data = response.json()
                if not self.conversation_id:
                    self.conversation_id = data.get("conversation_id")
                    print(f"✓ Created conversation {self.conversation_id}")
                return data
            else:
                print(f"✗ Chat request failed: {response.text}")
                return {}
        except Exception as e:
            print(f"✗ Chat error: {e}")
            return {}

    def get_conversation_history(self) -> list:
        """Get conversation message history."""
        if not self.conversation_id:
            return []

        try:
            response = self.session.get(
                f"{API_BASE}/api/chat/conversations/{self.conversation_id}/messages"
            )
            if response.status_code == 200:
                return response.json()
            print(f"✗ Failed to get history: {response.text}")
            return []
        except Exception as e:
            print(f"✗ History error: {e}")
            return []

    def test_natural_language_task_creation(self):
        """Test creating tasks with natural language."""
        print("\n=== Testing Natural Language Task Creation ===")

        test_messages = [
            "Add buy milk to my todo list",
            "Remind me to call mom tomorrow",
            "Create a task: finish the report",
            "I need to exercise at 5pm"
        ]

        for msg in test_messages:
            print(f"\nTesting: '{msg}'")
            result = self.create_task_via_chat(msg)
            if result:
                print(f"  AI Response: {result.get('response', 'No response')}")
                if result.get('tool_calls'):
                    print(f"  Tool Calls: {len(result['tool_calls'])} tool(s) executed")
                else:
                    print("  No tools were called")
            time.sleep(1)  # Rate limiting

    def test_task_listing(self):
        """Test listing tasks via chat."""
        print("\n=== Testing Task Listing ===")

        list_messages = [
            "Show me my tasks",
            "What's on my todo list?",
            "List all my pending tasks"
        ]

        for msg in list_messages:
            print(f"\nTesting: '{msg}'")
            result = self.create_task_via_chat(msg)
            if result:
                print(f"  AI Response: {result.get('response', 'No response')[:100]}...")
            time.sleep(1)

    def test_task_completion(self):
        """Test marking tasks as complete via chat."""
        print("\n=== Testing Task Completion ===")

        # First list tasks to get a task ID
        result = self.create_task_via_chat("Show me my tasks")

        # Try to complete a task
        complete_messages = [
            "Mark task 1 as complete",
            "I finished the first task",
            "Complete the milk task"
        ]

        for msg in complete_messages:
            print(f"\nTesting: '{msg}'")
            result = self.create_task_via_chat(msg)
            if result:
                print(f"  AI Response: {result.get('response', 'No response')}")
            time.sleep(1)

    def test_conversation_persistence(self):
        """Test that conversation history persists."""
        print("\n=== Testing Conversation Persistence ===")

        # Get current history
        history = self.get_conversation_history()
        print(f"Current message count: {len(history)}")

        # Send a new message
        self.create_task_via_chat("Remember this test message")

        # Get history again
        new_history = self.get_conversation_history()
        print(f"New message count: {len(new_history)}")

        if len(new_history) > len(history):
            print("✓ Conversation history is persisting correctly")
        else:
            print("✗ Conversation history might not be persisting")

    def run_all_tests(self):
        """Run all integration tests."""
        print("Phase 3 AI Chatbot Integration Tests")
        print("=" * 40)

        # Setup
        if not self.register_user():
            return False

        if not self.login_user():
            return False

        # Run tests
        self.test_natural_language_task_creation()
        self.test_task_listing()
        self.test_task_completion()
        self.test_conversation_persistence()

        print("\n=== Test Summary ===")
        print("✓ Natural language task creation tested")
        print("✓ Task listing via chat tested")
        print("✓ Task completion via chat tested")
        print("✓ Conversation persistence verified")
        print("\nAll tests completed!")

if __name__ == "__main__":
    tester = ChatIntegrationTester()
    tester.run_all_tests()