"""Run production database migration"""
import os
import subprocess
import sys

# Set the production DATABASE_URL
# Use the exact URL from .env but with postgresql+asyncpg://
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_3DbyqCvjPnN7@ep-mute-hill-agz5np87-pooler.c-2.eu-central-1.aws.neon.tech/neondb"

os.environ['DATABASE_URL'] = DATABASE_URL

print("=" * 60)
print("RUNNING PRODUCTION DATABASE MIGRATION")
print("=" * 60)
print(f"Database: Neon (eu-central-1)")
print(f"Migration: 004_fix_message_role_enum_to_varchar.py")
print("=" * 60)
print()

# First, stamp the database to 5e990c3ddfe4 (the revision before our fix)
print("Step 1: Stamping database to revision 5e990c3ddfe4...")
stamp_result = subprocess.run(
    ['alembic', 'stamp', '5e990c3ddfe4'],
    capture_output=True,
    text=True,
    check=False
)
print(stamp_result.stdout)
if stamp_result.stderr:
    print("STDERR:", stamp_result.stderr)

print("\nStep 2: Running migration 004 to fix message_role ENUM...")

# Run alembic upgrade
try:
    result = subprocess.run(
        ['alembic', 'upgrade', 'head'],
        capture_output=True,
        text=True,
        check=False
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    if result.returncode == 0:
        print()
        print("=" * 60)
        print("✓ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print()
        print("Testing chat API...")

        # Test the chat API
        import requests
        BACKEND = 'https://backend-kvm8wghw0-hamdanprofessionals-projects.vercel.app'

        # Login
        r = requests.post(f'{BACKEND}/api/auth/login',
                         json={'email': 'test1@test.com', 'password': 'Test1234'})

        if r.status_code == 200:
            token = r.json()['access_token']
            # Send chat
            chat = requests.post(f'{BACKEND}/api/chat',
                                json={'message': 'Migration test - hello!'},
                                headers={'Authorization': f'Bearer {token}'})

            if chat.status_code == 200:
                print("✓ Chat API is now working!")
                print()
                print("You can now test at:")
                print("https://frontend-hamdanprofessionals-projects.vercel.app/chat")
            else:
                print(f"✗ Chat still failing: {chat.status_code}")
                print(chat.json())
        else:
            print(f"✗ Login failed: {r.status_code}")
    else:
        print()
        print("=" * 60)
        print("✗ MIGRATION FAILED")
        print("=" * 60)
        sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
