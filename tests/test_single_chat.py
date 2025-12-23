#!/usr/bin/env python3
"""Single chat test"""
import requests
import json

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

# Login
response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
    "email": "testex@test.com",
    "password": "test1234"
})

token = response.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# Single chat request
print("Sending: 'List my tasks'")
response = requests.post(
    f"{BACKEND_URL}/api/chat",
    headers=headers,
    json={"message": "List my tasks"}
)

print(f"\nStatus: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\nResponse: {data.get('response', '')[:300]}")
    print(f"\nTool calls: {json.dumps(data.get('tool_calls', []), indent=2)}")

    # Check for fallback
    if "technical difficulties" in data.get('response', '').lower():
        print("\n[!] FALLBACK MODE DETECTED!")
    elif data.get('tool_calls'):
        print("\n[OK] MCP tools are working!")
    else:
        print("\n[?] No tool calls, no fallback - AI responded but didn't use tools")
else:
    print(f"Error: {response.text}")
