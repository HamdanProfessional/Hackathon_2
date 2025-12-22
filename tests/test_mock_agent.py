#!/usr/bin/env python3
"""
Test script with mock agent to confirm list_tasks works
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.ai.agent_mock import MockAgentService
from sqlalchemy import select

async def test_with_mock_agent():
    """Test with mock agent to bypass AI API issues"""

    print("=== Testing with Mock Agent ===")

    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(select(User).where(User.email == "chat_test@example.com"))
        user = result.scalar_one_or_none()

        if not user:
            print("Test user not found")
            return

        print(f"Testing with user: {user.email} (ID: {user.id})")

        # Use mock agent
        agent = MockAgentService()

        try:
            result = await agent.process_message(
                db=db,
                user_id=str(user.id),
                user_message="show my tasks",
                conversation_id=None
            )

            print(f"\nMock Agent response: {result['response']}")
            print(f"Tool calls made: {result.get('tool_calls', [])}")

            # Check if list_tasks was called
            if result.get('tool_calls'):
                for tool_call in result['tool_calls']:
                    if tool_call['name'] == 'list_tasks':
                        print("\n✅ list_tasks was called successfully!")
                        # The mock agent should have received the list_tasks result
                        break
                else:
                    print("\n❌ list_tasks was not called")
            else:
                print("\n❌ No tool calls were made")

        except Exception as e:
            print(f"Error in mock agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_with_mock_agent())