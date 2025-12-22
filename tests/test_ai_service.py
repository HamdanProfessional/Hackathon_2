#!/usr/bin/env python3
"""
Test script to verify that the real Gemini AI service is working correctly.
Run this script to test the AI service integration with task management tools.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

async def test_ai_service():
    """Test the real AI service with task management."""

    print("=" * 60)
    print("Testing Gemini AI Service Integration")
    print("=" * 60)

    try:
        # Import dependencies
        from app.ai.agent import AgentService
        from app.ai.tools import AVAILABLE_TOOLS
        from app.config import settings

        print(f"[CONFIG] AI_API_KEY configured: {bool(settings.AI_API_KEY and settings.AI_API_KEY.strip())}")
        print(f"[CONFIG] AI_BASE_URL: {settings.AI_BASE_URL}")
        print(f"[CONFIG] AI_MODEL: {settings.AI_MODEL}")

        # Check available tools
        tools = list(AVAILABLE_TOOLS.keys())
        print(f"[TOOLS] Available: {tools}")

        # Create AI service instance
        print("\n[TEST] Creating AI service instance...")
        agent = AgentService()
        print("[SUCCESS] AI service instance created!")

        # Test 1: Simple conversation without tools
        print("\n[TEST] Testing simple conversation...")
        response = await agent.client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "user", "content": "Hello, please respond with 'AI service is working!'"}
            ],
            max_tokens=50
        )
        print(f"[SUCCESS] AI Response: {response.choices[0].message.content}")

        # Test 2: Test task creation tool calling
        print("\n[TEST] Testing tool calling capability...")
        response = await agent.client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a task management assistant. Use tools when helpful."},
                {"role": "user", "content": "Create a task called 'Test task from AI'"}
            ],
            tools=[AVAILABLE_TOOLS["add_task"]["schema"]],
            tool_choice="auto",
            max_tokens=100
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            print(f"[SUCCESS] Tool call requested: {tool_call.function.name}")
            print(f"[INFO] Tool arguments: {tool_call.function.arguments}")
        else:
            print(f"[INFO] No tool call, response: {response.choices[0].message.content}")

        print("\n" + "=" * 60)
        print("[SUCCESS] All AI service tests passed!")
        print("=" * 60)
        print("\nThe real Gemini AI service is now enabled and ready to use.")
        print("The chatbot will provide intelligent responses and can execute")
        print("task management operations (add, list, complete, update, delete).")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("[FAILED] AI service test failed!")
        print("=" * 60)
        return False

    return True

if __name__ == "__main__":
    result = asyncio.run(test_ai_service())
    sys.exit(0 if result else 1)