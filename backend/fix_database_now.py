#!/usr/bin/env python3
"""
Emergency Database Fix Script for Production
Fixes UUID schema mismatch by recreating tables
"""

import asyncio
import os
from sqlalchemy import text
from app.database import engine

async def fix_database():
    """Fix the database schema by dropping and recreating tables with UUID columns."""
    print("🔧 Starting emergency database fix...")
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        async with engine.begin() as conn:
            print("⚡ Dropping existing tables...")
            
            # Drop existing tables
            await conn.execute(text("DROP TABLE IF EXISTS messages CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS conversations CASCADE"))
            print("✅ Tables dropped successfully")
            
            print("🏗️  Recreating tables with UUID columns...")
            
            # Recreate conversations table with UUID columns
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
            
            # Recreate messages table with UUID columns
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
            print("✅ Tables recreated with UUID columns")
            
            print("🧪 Testing the fix...")
            
            # Test the fix by inserting a test conversation
            result = await conn.execute(text("""
                INSERT INTO conversations (id, user_id, title) VALUES
                (gen_random_uuid(), '4b5bf227-e77c-474c-a57a-09fce5f8c51c', 'Test Conversation')
                RETURNING id
            """))
            
            test_id = result.scalar()
            print(f"✅ Test successful! Created test conversation with ID: {test_id}")
            
            # Verify schema
            schema_check = await conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name IN ('conversations', 'messages') 
                AND column_name = 'id'
                ORDER BY table_name, column_name
            """))
            
            schemas = schema_check.fetchall()
            print("📊 Schema verification:")
            for table, dtype in schemas:
                print(f"   {table}.id: {dtype}")
            
        print("🎉 Database fix completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database())
    if success:
        print("✨ Database is now fixed! Conversation functionality should work.")
    else:
        print("💥 Fix failed! Manual intervention required.")
