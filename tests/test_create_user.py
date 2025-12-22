"""Test creating a user directly."""
import asyncio
from app.database import AsyncSessionLocal
from app.crud.user import create_user
from app.schemas.user import UserCreate

async def test_create_user():
    async with AsyncSessionLocal() as db:
        try:
            user_data = UserCreate(
                email="test@example.com",
                password="testpassword123"
            )
            user = await create_user(db, user_data)
            print(f"User created successfully: {user}")
        except Exception as e:
            print(f"Error creating user: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_create_user())