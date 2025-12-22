#!/usr/bin/env python3
"""Test how the agent calls the tools to identify the exact issue."""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.tools import add_task, list_tasks, complete_task, update_task, delete_task, set_tool_context, clear_tool_context


async def test_agent_call_patterns():
    """Test the exact way the agent calls the tools."""

    print("Testing agent call patterns...")
    print("=" * 60)

    # Simulate how the agent calls the tools

    # Pattern 1: list_tasks (db and user_id first)
    print("\n1. Testing list_tasks call pattern (agent style):")
    try:
        function_args = {"status": "pending"}  # Example args from AI
        db = None  # Would be real db session
        user_id = "test-user-123"

        # This is how agent calls it
        result = await list_tasks(
            db=db,
            user_id=user_id,
            **function_args
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Exception: {type(e).__name__}: {e}")

    # Pattern 2: complete_task (task_id first, then db and user_id)
    print("\n2. Testing complete_task call pattern (agent style):")
    try:
        function_args = {"task_id": 1}  # Example args from AI
        db = None  # Would be real db session
        user_id = "test-user-123"

        # This is how agent calls it
        result = await complete_task(
            **function_args,
            db=db,
            user_id=user_id
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Exception: {type(e).__name__}: {e}")

    # Pattern 3: delete_task (task_id first, then db and user_id)
    print("\n3. Testing delete_task call pattern (agent style):")
    try:
        function_args = {"task_id": 1}  # Example args from AI
        db = None  # Would be real db session
        user_id = "test-user-123"

        # This is how agent calls it
        result = await delete_task(
            **function_args,
            db=db,
            user_id=user_id
        )
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Exception: {type(e).__name__}: {e}")

    # Pattern 4: Test with global context (like the agent does)
    print("\n" + "=" * 60)
    print("Testing with global context setting (like agent):")

    print("\n4. Setting global context and calling without db/user_id:")
    set_tool_context(db="mock_db", user_id="test-user-123")

    try:
        # This should use the global context
        result = await list_tasks(status="pending")
        print(f"   list_tasks result: {result.get('status')} - {result.get('message')}")
    except Exception as e:
        print(f"   list_tasks exception: {type(e).__name__}: {e}")

    try:
        # This should use the global context
        result = await complete_task(task_id=1)
        print(f"   complete_task result: {result.get('status')} - {result.get('message')}")
    except Exception as e:
        print(f"   complete_task exception: {type(e).__name__}: {e}")

    try:
        # This should use the global context
        result = await delete_task(task_id=1)
        print(f"   delete_task result: {result.get('status')} - {result.get('message')}")
    except Exception as e:
        print(f"   delete_task exception: {type(e).__name__}: {e}")

    clear_tool_context()

    # Pattern 5: Test with both global context AND explicit parameters
    print("\n5. Testing with global context AND explicit parameters:")
    set_tool_context(db="mock_db", user_id="test-user-123")

    try:
        # Both global and explicit - should use explicit
        result = await complete_task(task_id=1, db=None, user_id="explicit-user")
        print(f"   Result: {result.get('status')} - {result.get('message')}")
    except Exception as e:
        print(f"   Exception: {type(e).__name__}: {e}")

    clear_tool_context()

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_agent_call_patterns())