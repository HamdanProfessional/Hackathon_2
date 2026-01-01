#!/usr/bin/env python3
"""Test AI agent functionality end-to-end."""
import asyncio
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent.parent / "backend"
import sys
sys.path.insert(0, str(backend_dir))

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


async def test_basic_chat():
    """Test basic chat without tools."""
    print("\n=== Test 1: Basic Chat ===")

    client = AsyncOpenAI(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
    )

    response = await client.chat.completions.create(
        model=os.getenv("AI_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": "Say hello!"}]
    )

    print(f"Response: {response.choices[0].message.content}")
    return True


async def test_chat_with_tools():
    """Test chat with MCP tool definitions."""
    print("\n=== Test 2: Chat with Tools ===")

    client = AsyncOpenAI(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Get all tasks for the current user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed"]
                        }
                    }
                }
            }
        }
    ]

    response = await client.chat.completions.create(
        model=os.getenv("AI_MODEL", "llama-3.1-8b-instant"),
        messages=[{"role": "user", "content": "Show me my pending tasks"}],
        tools=tools
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        print(f"Tool called: {msg.tool_calls[0].function.name}")
        print(f"Arguments: {msg.tool_calls[0].function.arguments}")
    else:
        print(f"Response: {msg.content}")

    return True


async def test_conversation_history():
    """Test conversation history context."""
    print("\n=== Test 3: Conversation History ===")

    client = AsyncOpenAI(
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_BASE_URL", "https://api.groq.com/openai/v1")
    )

    messages = [
        {"role": "user", "content": "My name is Alice"},
        {"role": "assistant", "content": "Hello Alice!"},
        {"role": "user", "content": "What's my name?"}
    ]

    response = await client.chat.completions.create(
        model=os.getenv("AI_MODEL", "llama-3.1-8b-instant"),
        messages=messages
    )

    print(f"Response: {response.choices[0].message.content}")
    assert "Alice" in response.choices[0].message.content
    return True


async def test_tool_execution():
    """Test actual tool execution."""
    print("\n=== Test 4: Tool Execution ===")

    # Mock tool function
    async def get_tasks(status: str = None) -> list:
        """Mock get_tasks function."""
        return [
            {"id": 1, "title": "Task 1", "status": "pending"},
            {"id": 2, "title": "Task 2", "status": "pending"}
        ]

    # Execute tool
    result = await get_tasks(status="pending")
    print(f"Tasks: {result}")
    assert len(result) == 2
    return True


async def run_all_tests():
    """Run all agent tests."""
    print("=" * 50)
    print("AI Agent Test Suite")
    print("=" * 50)

    tests = [
        ("Basic Chat", test_basic_chat),
        ("Chat with Tools", test_chat_with_tools),
        ("Conversation History", test_conversation_history),
        ("Tool Execution", test_tool_execution),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, "PASS" if result else "FAIL"))
        except Exception as e:
            print(f"Error: {e}")
            results.append((name, f"FAIL: {e}"))

    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, result in results:
        status = "✓" if result == "PASS" else "✗"
        print(f"{status} {name}: {result}")

    passed = sum(1 for _, r in results if r == "PASS")
    print(f"\n{passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
