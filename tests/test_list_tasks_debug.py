#!/usr/bin/env python3
"""
Test script to debug list_tasks function issue
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.tools import list_tasks, set_tool_context, clear_tool_context
from app.database import get_db
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from sqlalchemy import select, text

async def test_list_tasks_directly():
    """Test list_tasks function directly to see the exact error"""

    # Use the same database setup as the main application
    from app.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as db:
            # First, let's check if we have a user and tasks
            print("\n=== Checking Database Schema ===")

            # Check priorities table
            try:
                result = await db.execute(text('SELECT id, name, level FROM priorities ORDER BY level'))
                priorities = result.all()
                print(f"Priorities in database ({len(priorities)} rows):")
                for p in priorities:
                    print(f"  ID: {p[0]}, Name: {p[1]}, Level: {p[2]}")
            except Exception as e:
                print(f"Error querying priorities: {e}")
                # Try to create priorities if they don't exist
                try:
                    print("\nAttempting to create priorities...")
                    await db.execute(text('''
                        INSERT INTO priorities (id, name, level, color) VALUES
                        (1, 'low', 1, '#28a745'),
                        (2, 'medium', 2, '#ffc107'),
                        (3, 'high', 3, '#dc3545')
                        ON CONFLICT (id) DO NOTHING
                    '''))
                    await db.commit()
                    print("Priorities created successfully")
                except Exception as e2:
                    print(f"Could not create priorities: {e2}")

            # Check tasks table
            try:
                result = await db.execute(text('SELECT COUNT(*) FROM tasks'))
                task_count = result.scalar()
                print(f"\nTasks in database: {task_count}")

                if task_count > 0:
                    result = await db.execute(text('''
                        SELECT t.id, t.title, t.priority_id, u.email
                        FROM tasks t
                        JOIN users u ON t.user_id = u.id
                        LIMIT 5
                    '''))
                    tasks = result.all()
                    print("Sample tasks:")
                    for t in tasks:
                        print(f"  ID: {t[0]}, Title: {t[1]}, Priority ID: {t[2]}, User: {t[3]}")
            except Exception as e:
                print(f"Error querying tasks: {e}")

            # Get a test user
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()

            if not user:
                print("\nNo users found in database!")
                return

            print(f"\n=== Testing list_tasks for user: {user.email} ===")
            print(f"User ID: {user.id}")

            # Set tool context
            set_tool_context(db, str(user.id))

            try:
                # Test list_tasks with no filters
                print("\n--- Test 1: list_tasks() with no filters ---")
                result = await list_tasks()
                print(f"Result: {result}")

                if result.get("status") == "error":
                    print(f"ERROR: {result.get('message')}")
                else:
                    print(f"SUCCESS: Found {result.get('count', 0)} tasks")
                    for task in result.get("tasks", []):
                        print(f"  - {task.get('title')} (Priority: {task.get('priority')}, Completed: {task.get('completed')})")

            except Exception as e:
                print(f"EXCEPTION in list_tasks: {e}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")

            finally:
                # Clear context
                clear_tool_context()

    finally:
        pass

if __name__ == "__main__":
    asyncio.run(test_list_tasks_directly())