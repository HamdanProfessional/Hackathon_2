"""Debug script to test list_tasks directly and via AI"""
import requests
import json

BACKEND = 'https://backend-k4t2o36f2-hamdanprofessionals-projects.vercel.app'

print("=" * 70)
print("DEBUG: Testing list_tasks functionality")
print("=" * 70)

# Login
login = requests.post(f'{BACKEND}/api/auth/login', json={'email': 'test1@test.com', 'password': 'Test1234'})
token = login.json()['access_token']
print(f"Token: {token[:30]}...")
print()

# Test 1: Get tasks via direct API
print("[TEST 1] Get tasks via direct /api/tasks endpoint")
tasks_response = requests.get(
    f'{BACKEND}/api/tasks',
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Status: {tasks_response.status_code}")
if tasks_response.status_code == 200:
    tasks = tasks_response.json()
    print(f"Tasks count: {len(tasks)}")
    for task in tasks[:3]:
        print(f"  - {task.get('title', 'No title')} (id={task.get('id')})")
else:
    print(f"Error: {tasks_response.text}")
print()

# Test 2: Try asking AI for tasks in a different way
print("[TEST 2] Ask AI: 'How many tasks do I have?'")
chat = requests.post(
    f'{BACKEND}/api/chat',
    json={'message': 'How many tasks do I have?'},
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Status: {chat.status_code}")
if chat.status_code == 200:
    response = chat.json()
    print(f"Response: {response.get('response', 'No response')[:200]}")
    print(f"Tool calls: {response.get('tool_calls', [])}")
else:
    print(f"Error: {chat.json()}")
print()

# Test 3: Try a simpler AI prompt
print("[TEST 3] Ask AI: 'List tasks'")
chat = requests.post(
    f'{BACKEND}/api/chat',
    json={'message': 'List tasks'},
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Status: {chat.status_code}")
if chat.status_code == 200:
    response = chat.json()
    print(f"Response: {response.get('response', 'No response')[:200]}")
    print(f"Tool calls: {response.get('tool_calls', [])}")
else:
    print(f"Error: {chat.json()}")
print()

# Test 4: Try with explicit tool call in prompt
print("[TEST 4] Ask AI: 'Use the list_tasks tool to show my tasks'")
chat = requests.post(
    f'{BACKEND}/api/chat',
    json={'message': 'Use the list_tasks tool to show my tasks'},
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Status: {chat.status_code}")
if chat.status_code == 200:
    response = chat.json()
    print(f"Response: {response.get('response', 'No response')[:200]}")
    print(f"Tool calls: {response.get('tool_calls', [])}")
else:
    print(f"Error: {chat.json()}")
print()

print("=" * 70)
print("DEBUG COMPLETE")
print("=" * 70)
