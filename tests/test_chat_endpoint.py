#!/usr/bin/env python3
"""
Test script to debug chat endpoint issue
"""

import asyncio
import sys
import os
import httpx
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.ai.agent import AgentService

async def test_chat_with_ai_service():
    """Test the chat endpoint/AI service directly"""

    backend_url = "https://backend-hamdanprofessionals-projects.vercel.app"

    # Test credentials - using known user
    email = "chat_test@example.com"
    password = "testpass123"

    # Get auth token
    async with httpx.AsyncClient() as client:
        # Login to get token
        login_response = await client.post(
            f"{backend_url}/api/auth/login",
            json={"email": email, "password": password}
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return

        token_data = login_response.json()
        access_token = token_data["access_token"]
        print(f"Successfully logged in as {email}")

        # Test chat message
        headers = {"Authorization": f"Bearer {access_token}"}
        chat_message = {"message": "show my tasks"}

        print(f"\n=== Testing chat endpoint ===")
        print(f"Message: {chat_message['message']}")

        chat_response = await client.post(
            f"{settings.BACKEND_URL}/api/chat/",
            json=chat_message,
            headers=headers
        )

        print(f"\nResponse status: {chat_response.status_code}")

        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"Response: {response_data['response']}")
            print(f"Tool calls: {response_data.get('tool_calls', [])}")

            # If tool calls were made, let's examine them
            if response_data.get('tool_calls'):
                print("\nTool calls details:")
                for tool_call in response_data['tool_calls']:
                    print(f"  - {tool_call['name']}: {tool_call['arguments']}")
        else:
            print(f"Error response: {chat_response.text}")

async def test_ai_agent_directly():
    """Test the AI agent service directly"""

    from app.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select

    print("\n=== Testing AI Agent directly ===")

    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(select(User).where(User.email == "chat_test@example.com"))
        user = result.scalar_one_or_none()

        if not user:
            print("Test user not found")
            return

        print(f"Testing with user: {user.email} (ID: {user.id})")

        # Check if AI is configured
        if not settings.AI_API_KEY:
            print("AI_API_KEY not configured, using mock agent")
            from app.ai.agent_mock import MockAgentService
            agent = MockAgentService()
        else:
            print("Using real AI agent")
            agent = AgentService()

        try:
            result = await agent.process_message(
                db=db,
                user_id=str(user.id),
                user_message="show my tasks",
                conversation_id=None
            )

            print(f"\nAgent response: {result['response']}")
            print(f"Tool calls: {result.get('tool_calls', [])}")

        except Exception as e:
            print(f"Error in agent: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")

async def main():
    # Use a default backend URL for testing
    backend_url = "https://backend-hamdanprofessionals-projects.vercel.app"
    print(f"Testing with backend URL: {backend_url}")
    await test_chat_with_ai_service()
    # Also test agent directly
    await test_ai_agent_directly()

if __name__ == "__main__":
    asyncio.run(main())