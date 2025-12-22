#!/usr/bin/env python3
"""Test script to check priorities table and debug list_tasks issue."""

import asyncio
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal, engine
from sqlalchemy import text
from app.crud import task as task_crud
from app.models.task import Priority

async def test_priorities():
    """Test if priorities table exists and has data."""
    print("=== Testing Priorities Table ===")
    try:
        async with AsyncSessionLocal() as db:
            # Check if priorities table exists in PostgreSQL
            result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'priorities'"))
            table_exists = result.fetchone()

            if table_exists:
                print("[OK] Priorities table exists (PostgreSQL)")

                # Check priorities data
                result = await db.execute(text("SELECT * FROM priorities"))
                priorities = result.fetchall()
                print(f"[OK] Found {len(priorities)} priorities:")
                for p in priorities:
                    print(f"  ID: {p[0]}, Name: {p[1]}, Level: {p[2]}")
            else:
                print("[ERROR] Priorities table not found in PostgreSQL!")
    except Exception as e:
        print(f"[ERROR] Error checking priorities: {e}")
        import traceback
        traceback.print_exc()

async def test_list_tasks():
    """Test the list_tasks function directly."""
    print("\n=== Testing list_tasks Directly ===")
    try:
        from app.ai.tools import list_tasks, set_tool_context, clear_tool_context

        async with AsyncSessionLocal() as db:
            # Set a test user_id (you may need to update this)
            test_user_id = "test-user-id"

            # Set tool context
            set_tool_context(db, test_user_id)

            try:
                # Call list_tasks
                result = await list_tasks()
                print(f"[OK] list_tasks returned: {result}")

                if result.get("status") == "success":
                    print(f"[OK] Found {result.get('count', 0)} tasks")
                    for task in result.get("tasks", [])[:3]:  # Show first 3 tasks
                        print(f"  - {task.get('title')} (Priority: {task.get('priority')})")
                else:
                    print(f"[ERROR] list_tasks failed: {result.get('message')}")

            finally:
                clear_tool_context()
    except Exception as e:
        print(f"[ERROR] Error testing list_tasks: {e}")
        import traceback
        traceback.print_exc()

async def test_task_crud():
    """Test the task CRUD directly."""
    print("\n=== Testing Task CRUD Directly ===")
    try:
        async with AsyncSessionLocal() as db:
            # Test get_tasks_by_user
            test_user_id = "test-user-id"
            tasks = await task_crud.get_tasks_by_user(db=db, user_id=test_user_id, limit=5)
            print(f"[OK] get_tasks_by_user returned {len(tasks)} tasks")

            for task in tasks[:3]:  # Show first 3 tasks
                print(f"  - Task ID: {task.id}, Title: {task.title}")
                print(f"    Priority ID: {task.priority_id}")
                if hasattr(task, 'priority_obj') and task.priority_obj:
                    print(f"    Priority Obj: {task.priority_obj.name}")
                else:
                    print(f"    Priority Obj: Not loaded")
    except Exception as e:
        print(f"[ERROR] Error testing task CRUD: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests."""
    print("Starting debug tests...\n")

    await test_priorities()
    await test_task_crud()
    await test_list_tasks()

    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(main())