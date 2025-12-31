import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"API Key (first 20): {api_key[:20]}..." if api_key else "ERROR: API Key is None!")

    client = AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    try:
        # Test 1: Simple message without tools
        print("\n=== Test 1: Simple message ===")
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello"}]
        )
        print(f"SUCCESS: {response.choices[0].message.content}")

        # Test 2: Message with tools (function calling)
        print("\n=== Test 2: Message with tools ===")
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "create a task called test"}],
            tools=[{
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"}
                        },
                        "required": ["title"]
                    }
                }
            }],
            tool_choice="auto"
        )
        print(f"SUCCESS: {response.choices[0].message.content}")
        if response.choices[0].message.tool_calls:
            print(f"Tool calls: {[tc.function.name for tc in response.choices[0].message.tool_calls]}")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

        # Test 3: Try with a different model
        print("\n=== Test 3: Try llama-3.1-8b-instant ===")
        try:
            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Say hello"}]
            )
            print(f"SUCCESS: {response.choices[0].message.content}")
        except Exception as e2:
            print(f"ERROR: {type(e2).__name__}: {e2}")

if __name__ == "__main__":
    asyncio.run(test_groq())
