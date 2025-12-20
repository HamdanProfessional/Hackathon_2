"""Test Phase 3 Chat functionality end-to-end."""
import asyncio
import httpx
from app.database import AsyncSessionLocal
from app.crud.user import create_user
from app.crud.auth import authenticate_user, create_access_token
from app.schemas.user import UserCreate

async def test_chat_integration():
    """Test the complete chat flow with authentication."""
    print("=== Phase 3 Chat Integration Test ===\n")

    # 1. Create a test user
    print("1. Creating test user...")
    async with AsyncSessionLocal() as db:
        user_data = UserCreate(
            email="chat_test@example.com",
            password="testpassword123",
            name="Chat Test User"
        )
        user = await create_user(db, user_data)
        print(f"   ✓ User created: {user.email} (ID: {user.id})")

    # 2. Authenticate and get JWT token
    print("\n2. Authenticating user...")
    async with AsyncSessionLocal() as db:
        authenticated = await authenticate_user(db, "chat_test@example.com", "testpassword123")
        if authenticated:
            token = create_access_token(data={"sub": authenticated.email})
            print(f"   ✓ Authentication successful")
            print(f"   ✓ JWT token generated: {token[:50]}...")
        else:
            print("   ✗ Authentication failed")
            return False

    # 3. Test chat endpoint
    print("\n3. Testing chat endpoint...")
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # First, let's check if the server is running
        try:
            response = await client.get("/")
            if response.status_code != 200:
                print(f"   ⚠ Server not running properly. Status: {response.status_code}")
                print("   Please start the server with: uvicorn app.main:app --reload --port 8000")
                return False
        except httpx.ConnectError:
            print("   ⚠ Server not running. Please start it with:")
            print("   uvicorn app.main:app --reload --port 8000")
            return False

        # Test chat endpoint
        chat_data = {
            "message": "Hello, I need to create a task",
            "conversation_id": None
        }

        try:
            response = await client.post("/api/chat", json=chat_data, headers=headers)

            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Chat request successful")
                print(f"   ✓ Response: {result.get('response', 'No response')[:100]}...")

                # Check if conversation was created
                if result.get("conversation_id"):
                    print(f"   ✓ Conversation created with ID: {result['conversation_id']}")

                return True
            else:
                print(f"   ✗ Chat request failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return False

        except Exception as e:
            print(f"   ✗ Error testing chat endpoint: {e}")
            return False

async def main():
    """Run the integration test."""
    print("Starting Phase 3 Chat Integration Test...\n")

    success = await test_chat_integration()

    print("\n=== Test Summary ===")
    if success:
        print("✅ All tests passed! Phase 3 chat functionality is working correctly.")
    else:
        print("❌ Some tests failed. Please check the logs above.")

    return success

if __name__ == "__main__":
    asyncio.run(main())