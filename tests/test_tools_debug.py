#!/usr/bin/env python3
"""Debug script to test tool functions directly."""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai.tools import add_task, list_tasks, complete_task, delete_task, set_tool_context, clear_tool_context
from app.database import get_db_session
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

async def test_tools():
    """Test all tool functions with a mock user."""

    # Create a database session
    async with get_db_session() as db:
        # Create a test user
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"  # Test UUID

        # Set tool context
        set_tool_context(db, test_user_id)

        print("\n=== Testing Tools ===\n")

        # Test 1: Create a task
        print("1. Creating a task...")
        result = await add_task(
            title="Test Task for Debug",
            description="This is a test task",
            priority="high"
        )
        print(f"   Result: {result}")

        if result.get("status") == "success":
            task_id = result.get("task_id")
            print(f"   Created task with ID: {task_id}")

            # Test 2: List tasks
            print("\n2. Listing tasks...")
            list_result = await list_tasks()
            print(f"   Result: {list_result}")

            # Test 3: Complete the task
            print("\n3. Completing the task...")
            complete_result = await complete_task(task_id=task_id)
            print(f"   Result: {complete_result}")

            # Test 4: Delete the task
            print("\n4. Deleting the task...")
            delete_result = await delete_task(task_id=task_id)
            print(f"   Result: {delete_result}")

            # Test 5: List tasks again to verify deletion
            print("\n5. Listing tasks after deletion...")
            final_list_result = await list_tasks()
            print(f"   Result: {final_list_result}")
        else:
            print("   ERROR: Failed to create task!")

        # Clear tool context
        clear_tool_context()

if __name__ == "__main__":
    print("Starting tool debug test...")
    asyncio.run(test_tools())
    print("\nDebug test completed.")
