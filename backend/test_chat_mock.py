"""Test chat with mock AI directly."""
import asyncio
import httpx

async def test_mock_chat():
    """Test the mock AI chat directly."""
    print("=== Testing Mock AI Chat ===\n")

    base_url = "http://localhost:8002"

    # Register/login
    user_data = {
        "email": "mock_test@example.com",
        "password": "testpassword123",
        "name": "Mock Test User"
    }

    async with httpx.AsyncClient(base_url=base_url) as client:
        # Try to login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = await client.post("/api/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"[OK] Login successful")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            # Register
            response = await client.post("/api/auth/register", json=user_data)
            if response.status_code == 201:
                token_data = response.json()
                token = token_data.get("access_token")
                print(f"[OK] Registration successful")
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print(f"[ERROR] Auth failed: {response.text}")
                return False

        # Test chat messages
        test_messages = [
            "Hello",
            "Create a task called 'Test task' with high priority",
            "List all my tasks"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Message {i}: {message} ---")
            chat_data = {
                "message": message,
                "conversation_id": None
            }

            response = await client.post("/api/chat/", json=chat_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', 'No response')
                print(f"Response: {response_text[:100]}...")
            else:
                print(f"Error: {response.status_code} - {response.text}")

        # Check tasks
        response = await client.get("/api/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"\n--- Tasks Found: {len(tasks)} ---")
            for task in tasks:
                print(f"- {task['title']} (Status: {task.get('completed', False)})")

    return True

if __name__ == "__main__":
    asyncio.run(test_mock_chat())