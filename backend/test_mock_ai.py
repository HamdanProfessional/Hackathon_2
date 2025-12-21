#!/usr/bin/env python3
"""
Test script for improved Mock AI Agent functionality
"""

import asyncio
from uuid import uuid4
from app.ai.agent_mock import MockAgentService

async def test_mock_agent():
    """Test various scenarios with the mock agent"""
    agent = MockAgentService()

    test_cases = [
        # Create task variations
        "Create a task called Finish the project",
        "Add a task to buy groceries",
        "I need to call mom tomorrow",
        "Remind me to finish the report with high priority",

        # List tasks variations
        "Show my tasks",
        "List all pending tasks",
        "What are my high priority tasks?",
        "Show tasks due today",

        # Complete task variations
        "Mark 'Finish the project' as complete",
        "I completed the shopping task",
        "Done with the homework",
        "Check off the meeting task",

        # Update task variations
        "Change priority of 'Finish project' to high",
        "Rename shopping task to grocery shopping",
        "Move the meeting to tomorrow",
        "Update the task description to include more details",

        # Delete task variations
        "Delete the old task",
        "Remove 'Finish project'",
        "Get rid of the shopping task",

        # Edge cases
        "Can you help me?",
        "What can you do?",
        "How do I create a task?",
        "I don't understand"
    ]

    print("=" * 80)
    print("TESTING IMPROVED MOCK AI AGENT")
    print("=" * 80)

    for i, message in enumerate(test_cases, 1):
        print(f"\nTest {i}: {message}")
        print("-" * 40)

        # Parse intent
        parsed = agent._parse_intent(message)
        print(f"Intent: {parsed['intent']}")
        print(f"Parameters: {parsed['parameters']}")

        # Simulate response without DB
        if parsed['intent'] == 'chat':
            response = agent._generate_chat_response(message)
            print(f"Response: {response[:100]}...")

    print("\n" + "=" * 80)
    print("TESTING DATE EXTRACTION")
    print("=" * 80)

    date_tests = [
        "Call mom tomorrow",
        "Meeting on Friday",
        "Due 12/25/2025",
        "Task due 2025-12-30",
        "In 3 days",
        "Next week"
    ]

    for date_test in date_tests:
        due_date = agent._extract_due_date(date_test.lower())
        print(f"'{date_test}' -> {due_date}")

    print("\n" + "=" * 80)
    print("TESTING TASK REFERENCE EXTRACTION")
    print("=" * 80)

    ref_tests = [
        "Complete the 'Finish project' task",
        "Delete shopping task",
        "Update 'buy groceries'",
        "Mark the meeting as done"
    ]

    for ref_test in ref_tests:
        task_ref = agent._extract_task_reference(ref_test)
        print(f"'{ref_test}' -> '{task_ref}'")

    print("\n" + "=" * 80)
    print("TESTING UPDATE EXTRACTION")
    print("=" * 80)

    update_tests = [
        "Change priority to high",
        "Rename to 'New Task Name'",
        "Update description to 'More details here'",
        "Move deadline to tomorrow",
        "Make it urgent"
    ]

    for update_test in update_tests:
        updates = agent._extract_updates(update_test)
        print(f"'{update_test}' -> {updates}")

if __name__ == "__main__":
    asyncio.run(test_mock_agent())