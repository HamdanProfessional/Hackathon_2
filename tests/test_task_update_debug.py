#!/usr/bin/env python3
"""
Debug Task Update API 400 Error
"""

import requests
import json
import time

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

# Test user
TIMESTAMP = int(time.time())
TEST_EMAIL = f"update{TIMESTAMP}@example.com"
TEST_PASSWORD = "UpdatePass123!"

def main():
    print("=" * 60)
    print("  Task Update API Debug Test")
    print("=" * 60)

    # Step 1: Login
    print("\n1. Login...")
    response = requests.post(f"{BACKEND_URL}/api/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "name": "Update Test"
    })

    if response.status_code not in [200, 201]:
        response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })

    if response.status_code not in [200, 201]:
        print(f"[FAIL] Login failed: {response.status_code}")
        print(response.text)
        return

    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] Logged in")

    # Step 2: Create a task
    print("\n2. Create task...")
    response = requests.post(
        f"{BACKEND_URL}/api/tasks",
        headers=headers,
        json={
            "title": "Test Task for Update",
            "description": "Testing update",
            "priority": "medium"
        }
    )

    if response.status_code not in [200, 201]:
        print(f"[FAIL] Create task failed: {response.status_code}")
        print(response.text)
        return

    task = response.json()
    task_id = task.get("id")
    print(f"[OK] Created task ID: {task_id}")
    print(f"      Task: {json.dumps(task, indent=2)}")

    # Step 3: Test UPDATE with different payloads
    print("\n3. Testing UPDATE with different payloads...")

    # Test 3.1: Update with completed=True
    print("\n  Test 3.1: PUT with completed=True")
    response = requests.put(
        f"{BACKEND_URL}/api/tasks/{task_id}",
        headers=headers,
        json={"completed": True}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text if response.status_code != 200 else 'OK'}")

    # Test 3.2: Update with PATCH (if exists)
    print("\n  Test 3.2: PATCH with completed=True")
    response = requests.patch(
        f"{BACKEND_URL}/api/tasks/{task_id}",
        headers=headers,
        json={"completed": True}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text if response.status_code != 200 else 'OK'}")

    # Test 3.3: Toggle completion endpoint
    print("\n  Test 3.3: PATCH /api/tasks/{id}/complete")
    response = requests.patch(
        f"{BACKEND_URL}/api/tasks/{task_id}/complete",
        headers=headers
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text if response.status_code != 200 else 'OK'}")

    # Step 4: Check what endpoints are available
    print("\n4. Checking available task endpoints...")
    print("\n  Available endpoints (from OpenAPI spec):")
    print("  - POST   /api/tasks - Create task")
    print("  - GET    /api/tasks - List tasks")
    print("  - GET    /api/tasks/{id} - Get task")
    print("  - PUT    /api/tasks/{id} - Update task")
    print("  - DELETE /api/tasks/{id} - Delete task")
    print("  - PATCH  /api/tasks/{id}/complete - Toggle completion")

if __name__ == "__main__":
    main()
