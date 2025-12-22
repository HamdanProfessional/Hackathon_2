"""Direct SQL fix for production database schema - bypass Alembic"""
import asyncio
import asyncpg

DATABASE_URL = "postgresql://neondb_owner:npg_3DbyqCvjPnN7@ep-mute-hill-agz5np87-pooler.c-2.eu-central-1.aws.neon.tech/neondb"

async def fix_schema():
    print("=" * 70)
    print("DIRECT SQL FIX FOR PRODUCTION DATABASE")
    print("=" * 70)
    print()

    # Connect to database
    print("Connecting to production database...")
    conn = await asyncpg.connect(DATABASE_URL)

    try:
        # Check if message_role ENUM exists
        print("\nStep 1: Checking for message_role ENUM type...")
        enum_check = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'message_role'
            );
        """)

        if enum_check:
            print("  [FOUND] message_role ENUM type exists")

            # Get current column type
            col_type = await conn.fetchval("""
                SELECT udt_name
                FROM information_schema.columns
                WHERE table_name = 'messages' AND column_name = 'role';
            """)
            print(f"  Current column type: {col_type}")

            if col_type == 'message_role':
                print("\nStep 2: Converting messages.role from ENUM to VARCHAR(20)...")

                # Convert column type
                await conn.execute("""
                    ALTER TABLE messages
                    ALTER COLUMN role TYPE VARCHAR(20)
                    USING role::text;
                """)
                print("  [SUCCESS] Column converted to VARCHAR(20)")

                print("\nStep 3: Adding CHECK constraint...")
                # Check if constraint exists
                constraint_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.constraint_column_usage
                        WHERE table_name = 'messages'
                        AND constraint_name = 'check_role_values'
                    );
                """)

                if not constraint_exists:
                    await conn.execute("""
                        ALTER TABLE messages
                        ADD CONSTRAINT check_role_values
                        CHECK (role IN ('user', 'assistant', 'system', 'tool'));
                    """)
                    print("  [SUCCESS] CHECK constraint added")
                else:
                    print("  [SKIP] CHECK constraint already exists")

                print("\nStep 4: Dropping message_role ENUM type...")
                await conn.execute("DROP TYPE message_role;")
                print("  [SUCCESS] ENUM type dropped")

                print("\n" + "=" * 70)
                print("MIGRATION COMPLETE!")
                print("=" * 70)

            else:
                print(f"\n [INFO] Column is already {col_type}, not ENUM")
                print("=" * 70)
                print("NO CHANGES NEEDED")
                print("=" * 70)
        else:
            print("  [INFO] No message_role ENUM found - schema already correct")
            print("\n" + "=" * 70)
            print("NO CHANGES NEEDED")
            print("=" * 70)

        # Test the fix
        print("\n" + "=" * 70)
        print("TESTING CHAT API...")
        print("=" * 70)

        import requests
        BACKEND = 'https://backend-kvm8wghw0-hamdanprofessionals-projects.vercel.app'

        # Login
        r = requests.post(f'{BACKEND}/api/auth/login',
                         json={'email': 'test1@test.com', 'password': 'Test1234'})

        if r.status_code == 200:
            token = r.json()['access_token']
            # Send chat
            chat = requests.post(f'{BACKEND}/api/chat',
                                json={'message': 'Schema fix test - hello!'},
                                headers={'Authorization': f'Bearer {token}'})

            if chat.status_code == 200:
                print("\n SUCCESS! Chat API is now working!")
                print("\nYou can now test at:")
                print("https://frontend-hamdanprofessionals-projects.vercel.app/chat")
                print()
            else:
                print(f"\n Chat still failing: {chat.status_code}")
                print(chat.json())
        else:
            print(f"\n Login failed: {r.status_code}")

    finally:
        await conn.close()
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(fix_schema())
