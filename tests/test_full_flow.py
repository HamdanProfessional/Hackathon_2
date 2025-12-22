#!/usr/bin/env python3
"""Test the full flow with actual database connection to identify real errors."""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai.tools import add_task, list_tasks, complete_task, delete_task, set_tool_context, clear_tool_context
from app.database import get_db, engine
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def get_test_db():
    """Get a test database session."""
    async for session in get_db():
        return session


async def test_with_real_database():
    """Test tools with a real database session to see actual errors."""

    print("Testing tools with real database connection...")
    print("=" * 60)

    # Get a real database session
    async with engine.begin() as conn:
        # Ensure we have a connection
        print("Database connection established")

    async for db in get_db():
        print(f"Got database session: {type(db)}")

        # Find a test user or create one
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("No users found in database - creating test user")
            import uuid
            test_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                hashed_password="test_hash"
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            print(f"Created test user: {test_user.id}")

        user_id = str(test_user.id)
        print(f"Using test user ID: {user_id}")

        # Test 1: Create a task first (this works according to user)
        print("\n1. Creating a test task:")
        try:
            result = await add_task(
                title="Test Task for Debugging",
                description="This is a test task",
                priority="high",
                db=db,
                user_id=user_id
            )
            print(f"   Result: {result}")
            if result.get('status') == 'success':
                task_id = result.get('task_id')
                print(f"   Created task with ID: {task_id}")
            else:
                print(f"   Failed to create task: {result.get('message')}")
                return
        except Exception as e:
            print(f"   Exception: {type(e).__name__}: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return

        # Test 2: List tasks (user said this fails)
        print("\n2. Listing tasks:")
        try:
            result = await list_tasks(
                db=db,
                user_id=user_id
            )
            print(f"   Result status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Count: {result.get('count')}")
            if result.get('tasks'):
                print(f"   Tasks found: {len(result['tasks'])}")
                for task in result['tasks'][:3]:  # Show first 3 tasks
                    print(f"   - Task {task['id']}: {task['title']}")
            else:
                print("   No tasks returned")
        except Exception as e:
            print(f"   Exception: {type(e).__name__}: {e}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")

        # Test 3: Complete task (user said this fails)
        if task_id:
            print(f"\n3. Completing task {task_id}:")
            try:
                result = await complete_task(
                    task_id=task_id,
                    db=db,
                    user_id=user_id
                )
                print(f"   Result status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
            except Exception as e:
                print(f"   Exception: {type(e).__name__}: {e}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")

        # Test 4: Create another task to delete
        print("\n4. Creating another task for deletion test:")
        try:
            result = await add_task(
                title="Task to Delete",
                description="This task will be deleted",
                db=db,
                user_id=user_id
            )
            print(f"   Result: {result}")
            if result.get('status') == 'success':
                delete_task_id = result.get('task_id')
                print(f"   Created task with ID: {delete_task_id}")

                # Test 5: Delete task (user said this fails)
                print(f"\n5. Deleting task {delete_task_id}:")
                try:
                    result = await delete_task(
                        task_id=delete_task_id,
                        db=db,
                        user_id=user_id
                    )
                    print(f"   Result status: {result.get('status')}")
                    print(f"   Message: {result.get('message')}")
                except Exception as e:
                    print(f"   Exception: {type(e).__name__}: {e}")
                    import traceback
                    print(f"   Traceback: {traceback.format_exc()}")
            else:
                print(f"   Failed to create task for deletion: {result.get('message')}")
        except Exception as e:
            print(f"   Exception creating task: {type(e).__name__}: {e}")

        # Test 6: Test with global context (like agent does)
        print("\n6. Testing with global context setting:")
        set_tool_context(db, user_id)

        try:
            result = await list_tasks(status="all")
            print(f"   list_tasks with global context - Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
        except Exception as e:
            print(f"   Exception: {type(e).__name__}: {e}")

        clear_tool_context()

        break  # Only need one db session

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(test_with_real_database())