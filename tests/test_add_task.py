#!/usr/bin/env python3
"""Test script to verify add_task tool functionality."""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.tools import add_task, set_tool_context, clear_tool_context
from app.database import get_db
from app.models.user import User
from app.crud.user import get_user_by_email
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select, text


async def test_add_task():
    """Test the add_task function."""
    print("Testing add_task function...")

    # Get a database session
    async for db in get_db():
        try:
            # Find a test user (first user in database)
            result = await db.execute(
                text("SELECT id FROM users LIMIT 1")
            )
            user_row = result.fetchone()

            if not user_row:
                print("ERROR: No users found in database")
                return False

            user_uuid = str(user_row[0])
            print(f"Using user UUID: {user_uuid}")

            # Set tool context
            set_tool_context(db, user_uuid)

            # Test adding a task
            print("\nTest 1: Adding a simple task")
            result = await add_task(
                title="Test Task from Script",
                description="This is a test task created by the test script"
            )
            print(f"Result: {result}")

            if result.get("status") == "success":
                print(f"[PASS] Task created successfully with ID: {result.get('task_id')}")
            else:
                print(f"[FAIL] Task creation failed: {result.get('message')}")
                return False

            # Test adding a task with priority and due date
            print("\nTest 2: Adding a task with priority and due date")
            result = await add_task(
                title="High Priority Task",
                description="This is a high priority task",
                priority="high",
                due_date="2025-12-25"
            )
            print(f"Result: {result}")

            if result.get("status") == "success":
                print(f"[PASS] Task created successfully with ID: {result.get('task_id')}")
            else:
                print(f"[FAIL] Task creation failed: {result.get('message')}")
                return False

            # Test adding a task with invalid priority (should default to medium)
            print("\nTest 3: Adding a task with invalid priority")
            result = await add_task(
                title="Task with Invalid Priority",
                description="This task should default to medium priority",
                priority="invalid_priority"
            )
            print(f"Result: {result}")

            if result.get("status") == "success":
                print(f"[PASS] Task created successfully (defaulted to medium) with ID: {result.get('task_id')}")
            else:
                print(f"[FAIL] Task creation failed: {result.get('message')}")
                return False

            print("\n[PASS] All tests passed!")
            return True

        except Exception as e:
            print(f"[FAIL] Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            clear_tool_context()


if __name__ == "__main__":
    success = asyncio.run(test_add_task())
    sys.exit(0 if success else 1)