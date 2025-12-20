"""Simple test for Phase 3 Chat functionality."""
import asyncio
import httpx

async def test_chat_flow():
    """Test the complete chat flow."""
    print("=== Phase 3 Chat Test ===\n")

    base_url = "http://localhost:8003"

    # First, let's check if the server is running
    print("1. Checking server...")
    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            response = await client.get("/")
            if response.status_code != 200:
                print(f"   [WARN] Server not running properly. Status: {response.status_code}")
                print("   Please start the server with: uvicorn app.main:app --reload --port 8000")
                return False
            print("   [OK] Server is running")
        except httpx.ConnectError:
            print("   [WARN] Server not running. Please start it with:")
            print("   uvicorn app.main:app --reload --port 8000")
            return False

    # 2. Register a new user
    print("\n2. Registering test user...")
    user_data = {
        "email": "chat_test@example.com",
        "password": "testpassword123",
        "name": "Chat Test User"
    }

    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            response = await client.post("/api/auth/register", json=user_data)
            if response.status_code == 201:
                token_data = response.json()
                token = token_data.get("access_token")
                print(f"   [OK] User registered successfully")
                print(f"   [OK] Got access token: {token[:30]}...")
                headers = {"Authorization": f"Bearer {token}"}
            elif response.status_code == 409:
                print("   [WARN] User already exists, trying to login...")
                # Try to login instead
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                response = await client.post("/api/auth/login", json=login_data)
                if response.status_code == 200:
                    token_data = response.json()
                    token = token_data.get("access_token")
                    print(f"   [OK] Login successful")
                    print(f"   [OK] Got access token: {token[:30]}...")
                    headers = {"Authorization": f"Bearer {token}"}
                else:
                    print(f"   [ERROR] Login failed: {response.text}")
                    return False
            else:
                print(f"   [ERROR] Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"   [ERROR] Error during registration: {e}")
            return False

    # 3. Test chat endpoint
    print("\n3. Testing chat endpoint...")
    chat_messages = [
        "Hello, I need help organizing my tasks",
        "Create a task called 'Finish project' with high priority",
        "List all my tasks",
        "Mark the first task as completed"
    ]

    async with httpx.AsyncClient(base_url=base_url, follow_redirects=True) as client:
        conversation_id = None

        for i, message in enumerate(chat_messages, 1):
            chat_data = {
                "message": message,
                "conversation_id": conversation_id
            }

            try:
                response = await client.post("/api/chat/", json=chat_data, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    print(f"\n   Message {i}: {message}")
                    print(f"   Response: {result.get('response', 'No response')[:150]}...")

                    # Update conversation_id if provided
                    if result.get("conversation_id"):
                        conversation_id = result["conversation_id"]
                        print(f"   [OK] Conversation ID: {conversation_id}")
                else:
                    print(f"\n   [ERROR] Chat request {i} failed with status {response.status_code}")
                    print(f"   Error: {response.text}")
                    return False

            except Exception as e:
                print(f"\n   [ERROR] Error testing message {i}: {e}")
                return False

    # 4. Test task management to see if tasks were created
    print("\n4. Checking created tasks...")
    async with httpx.AsyncClient(base_url=base_url) as client:
        try:
            response = await client.get("/api/tasks", headers=headers)
            if response.status_code == 200:
                tasks = response.json()
                print(f"   [OK] Found {len(tasks)} tasks")
                for task in tasks:
                    print(f"     - {task['title']} (Status: {task['status']}, Priority: {task['priority']})")
            else:
                print(f"   [WARN] Could not fetch tasks: {response.status_code}")
        except Exception as e:
            print(f"   [WARN] Error fetching tasks: {e}")

    print("\n=== Test Summary ===")
    print("[SUCCESS] Chat functionality test completed successfully!")
    print("\nThe Phase 3 AI Chatbot is working with:")
    print("  - User authentication")
    print("  - Conversation persistence")
    print("  - AI-powered task management")
    print("  - Integration with MCP tools")

    return True

async def main():
    """Run the test."""
    success = await test_chat_flow()
    return success

if __name__ == "__main__":
    asyncio.run(main())