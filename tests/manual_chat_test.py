#!/usr/bin/env python3
"""
Manual Chat Test to see actual chatbot responses
"""

import requests
import json

def test_chat_responses():
    backend_url = "https://backend-hamdanprofessionals-projects.vercel.app"

    # Register and login
    session = requests.Session()

    # Register
    register_payload = {
        "email": "chat_test@example.com",
        "password": "TestPassword123!",
        "name": "Chat Test User"
    }

    register_response = session.post(f"{backend_url}/api/auth/register", json=register_payload)
    print("Register response:", register_response.status_code, register_response.text[:200])

    # Login
    login_payload = {
        "email": "chat_test@example.com",
        "password": "TestPassword123!"
    }

    login_response = session.post(f"{backend_url}/api/auth/login", json=login_payload)
    print("Login response:", login_response.status_code)

    if login_response.status_code == 200:
        token_data = login_response.json()
        auth_token = token_data.get("access_token")
        session.headers.update({"Authorization": f"Bearer {auth_token}"})

        # Test various chat messages
        test_messages = [
            "Hello, what can you help me with?",
            "Create a task called 'Review project documentation'",
            "Show me all my tasks",
            "What AI model are you using?",
            "Help me organize my work for today",
            "What features do you have?"
        ]

        print("\n" + "="*50)
        print("CHATBOT RESPONSES")
        print("="*50)

        for i, message in enumerate(test_messages, 1):
            payload = {"message": message}
            response = session.post(f"{backend_url}/api/chat/", json=payload, timeout=30)

            print(f"\n{i}. User: {message}")
            if response.status_code == 200:
                chat_data = response.json()
                bot_response = chat_data.get("response", "")
                print(f"   Bot: {bot_response}")

                # Also check for tool calls
                tool_calls = chat_data.get("tool_calls", [])
                if tool_calls:
                    print(f"   Tool Calls: {json.dumps(tool_calls, indent=2)}")
                else:
                    print("   Tool Calls: None")
            else:
                print(f"   Error: HTTP {response.status_code} - {response.text}")
            print("-" * 40)

if __name__ == "__main__":
    test_chat_responses()