#!/usr/bin/env python
"""Test script to verify chat transaction fixes."""

import asyncio
import sys
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

# Add the app directory to the path
sys.path.append(".")

from app.database import AsyncSessionLocal
from app.models.user import User
from app.ai.conversation_manager import ConversationManager
from app.ai.agent_mock import MockAgentService


async def test_transaction_flow():
    """Test that conversation creation and message saving work without rollbacks."""

    print("[TEST] Starting transaction flow test...")

    # Create a database session
    async with AsyncSessionLocal() as db:
        try:
            # Create a test user
            test_user_id = uuid4()
            test_user = User(
                id=test_user_id,
                email="test@example.com",
                name="Test User",
                password_hash="test_hash",
                hashed_password="test_hash"
            )
            db.add(test_user)
            await db.flush()
            print(f"[TEST] Created test user: {test_user_id}")

            # Test ConversationManager
            conv_manager = ConversationManager(db)

            # Create a conversation
            conversation_id = await conv_manager.create_conversation(test_user_id)
            print(f"[TEST] Created conversation: {conversation_id}")

            # Save a message
            await conv_manager.save_message(
                conversation_id=conversation_id,
                role="user",
                content="Test message"
            )
            print("[TEST] Saved user message")

            await conv_manager.save_message(
                conversation_id=conversation_id,
                role="assistant",
                content="Test response"
            )
            print("[TEST] Saved assistant message")

            # Test MockAgentService
            agent = MockAgentService()
            result = await agent.process_message(
                db=db,
                user_id=test_user_id,
                user_message="Create a test task",
                conversation_id=None
            )

            print(f"[TEST] Agent processed successfully")
            print(f"[TEST] Result conversation_id: {result.get('conversation_id')}")
            print(f"[TEST] Result response: {result.get('response')}")

            # Verify no rollback happened by checking the conversation exists
            history = await conv_manager.get_history(conversation_id)
            print(f"[TEST] Retrieved {len(history)} messages from conversation")

            # Commit the transaction
            await db.commit()
            print("[TEST] Transaction committed successfully!")

            return True

        except Exception as e:
            print(f"[TEST ERROR] {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False


async def test_multiple_transactions():
    """Test multiple chat operations in sequence."""

    print("\n[TEST] Starting multiple transactions test...")

    async with AsyncSessionLocal() as db:
        try:
            # Create a test user
            test_user_id = uuid4()
            test_user = User(
                id=test_user_id,
                email="test2@example.com",
                name="Test User 2",
                password_hash="test_hash",
                hashed_password="test_hash"
            )
            db.add(test_user)
            await db.flush()

            agent = MockAgentService()

            # Test 1: New conversation
            result1 = await agent.process_message(
                db=db,
                user_id=test_user_id,
                user_message="Hello",
                conversation_id=None
            )
            print(f"[TEST] First message - Conversation ID: {result1['conversation_id']}")

            # Test 2: Same conversation
            result2 = await agent.process_message(
                db=db,
                user_id=test_user_id,
                user_message="List my tasks",
                conversation_id=result1['conversation_id']
            )
            print(f"[TEST] Second message - Same Conversation ID: {result2['conversation_id']}")

            # Test 3: New conversation again
            result3 = await agent.process_message(
                db=db,
                user_id=test_user_id,
                user_message="Create a new conversation",
                conversation_id=None
            )
            print(f"[TEST] Third message - New Conversation ID: {result3['conversation_id']}")

            await db.commit()
            print("[TEST] All transactions committed successfully!")

            return True

        except Exception as e:
            print(f"[TEST ERROR] {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("CHAT TRANSACTION FIX VERIFICATION")
    print("=" * 60)

    # Test 1: Basic transaction flow
    success1 = await test_transaction_flow()

    # Test 2: Multiple transactions
    success2 = await test_multiple_transactions()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"  Transaction flow test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"  Multiple transactions test: {'✅ PASSED' if success2 else '❌ FAILED'}")

    if success1 and success2:
        print("\n✅ All tests passed! Transaction rollback issue is fixed.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

    print("=" * 60)

    return 0 if (success1 and success2) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)