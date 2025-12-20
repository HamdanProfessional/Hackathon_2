"""Debug the Phase 3 chat test with detailed output."""
import asyncio
import httpx
import json

async def test_chat_debug():
    """Test chat with detailed debug output."""
    print("=== Phase 3 Chat Debug Test ===\n")

    base_url = "http://localhost:8003"

    # Register/login
    print("1. Login...")
    async with httpx.AsyncClient(base_url=base_url) as client:
        login_data = {
            "email": "chat_test@example.com",
            "password": "testpassword123",
            "name": "Chat Test User"
        }
        response = await client.post("/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   [OK] Got token")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            # Try register
            response = await client.post("/api/auth/register", json=login_data)
            if response.status_code == 201:
                token_data = response.json()
                token = token_data.get("access_token")
                print(f"   [OK] Registered and got token")
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print(f"   [ERROR] Auth failed: {response.text}")
                return

        # Test messages one by one
        test_messages = [
            "Hello",
            "Create a task called Test Task",
            "List all tasks",
            "What tasks do I have?"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing: '{message}'")
            chat_data = {
                "message": message,
                "conversation_id": None
            }

            response = await client.post("/api/chat/", json=chat_data, headers=headers)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result.get('response', 'No response')}")
                print(f"   Conv ID: {result.get('conversation_id')}")
                print(f"   Tool calls: {result.get('tool_calls', [])}")
            else:
                print(f"   Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_chat_debug())