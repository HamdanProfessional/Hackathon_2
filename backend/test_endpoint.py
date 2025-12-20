"""Test if the chat endpoint is reachable."""
import asyncio
import httpx

async def test_endpoint():
    """Test if chat endpoint is reachable."""
    base_url = "http://localhost:8003"

    async with httpx.AsyncClient(base_url=base_url) as client:
        # Test health endpoint
        print("Testing / endpoint...")
        try:
            response = await client.get("/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")

        # Test login
        print("\nTesting /api/auth/login...")
        login_data = {
            "email": "mock_test@example.com",
            "password": "testpassword123"
        }
        response = await client.post("/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"Got token: {token[:30]}...")

            # Test chat endpoint with multiple messages
            print("\nTesting /api/chat/...")
            test_messages = [
                "Hello",
                "Create a task called 'Test project' with high priority",
                "List all my tasks"
            ]
            conversation_id = None

            for msg in test_messages:
                chat_data = {
                    "message": msg,
                    "conversation_id": conversation_id
                }
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.post("/api/chat/", json=chat_data, headers=headers)
                print(f"\nMessage: {msg}")
                print(f"Status: {response.status_code}")
                result = response.json()
                print(f"Response: {result.get('response', 'No response')[:150]}...")
                conversation_id = result.get('conversation_id')
        else:
            print(f"Login failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())