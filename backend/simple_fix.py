import asyncio
import os
from sqlalchemy import text
from app.database import engine

async def fix_database():
    print("Starting database fix...")
    
    try:
        async with engine.begin() as conn:
            print("Dropping tables...")
            await conn.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE"))
            print("Tables dropped.")
            
            print("Recreating tables with UUID...")
            await conn.execute(text("""
                CREATE TABLE conversations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL,
                    title VARCHAR(200) NOT NULL DEFAULT 'New Conversation',
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """))
            
            await conn.execute(text("""
                CREATE TABLE messages (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    conversation_id UUID NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls JSONB,
                    tool_call_id VARCHAR(100),
                    name VARCHAR(100),
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """))
            print("Tables recreated with UUID.")
            
            print("Testing fix...")
            result = await conn.execute(text("""
                INSERT INTO conversations (id, user_id, title) VALUES
                (gen_random_uuid(), '4b5bf227-e77c-474c-a57a-09fce5f8c51c', 'Test')
                RETURNING id
            """))
            test_id = result.scalar()
            print(f"Test successful! ID: {test_id}")
            
        print("Database fix completed!")
        return True
        
    except Exception as e:
        print(f"Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database())
    print("SUCCESS" if success else "FAILED")
