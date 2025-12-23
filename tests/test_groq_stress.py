#!/usr/bin/env python3
"""
Stress test Groq API to check rate limiting
"""

import requests
import time
import asyncio

BACKEND_URL = "https://backend-p1lx7zgp8-hamdanprofessionals-projects.vercel.app"

TEST_EMAIL = "testex@test.com"
TEST_PASSWORD = "test1234"

def get_token():
    response = requests.post(f"{BACKEND_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    return response.json().get("access_token")

def test_chat(token, message, index):
    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()
    response = requests.post(
        f"{BACKEND_URL}/api/chat",
        headers=headers,
        json={"message": message}
    )
    elapsed = time.time() - start

    success = response.status_code == 200
    data = response.json() if success else None

    # Check if it's the "technical difficulties" fallback
    is_fallback = False
    if success and data:
        resp_text = data.get("response", "").lower()
        is_fallback = "technical difficulties" in resp_text

    return {
        "index": index,
        "status": response.status_code,
        "success": success,
        "is_fallback": is_fallback,
        "elapsed": elapsed,
        "has_tool_calls": bool(data.get("tool_calls")) if data else False,
        "response_preview": data.get("response", "")[:100] if data else response.text[:100]
    }

def main():
    print("""
====================================================
  Groq API Stress Test
====================================================""")

    token = get_token()
    print(f"[OK] Got token: {token[:20]}...")

    # Test 1: Sequential requests
    print("\n--- Test 1: 5 Sequential Requests ---")
    results = []
    for i in range(5):
        result = test_chat(token, "List my tasks", i)
        results.append(result)
        status_icon = "[OK]" if result["success"] else "[FAIL]"
        fallback_icon = "[FALLBACK]" if result["is_fallback"] else ""
        tool_icon = "[TOOLS]" if result["has_tool_calls"] else ""
        print(f"  Request {i+1}: {status_icon} {result['status']} {fallback_icon} {tool_icon} {result['elapsed']:.1f}s")
        if result["is_fallback"]:
            print(f"    → FALLBACK MODE: {result['response_preview']}")

    # Test 2: Quick succession (potential rate limit)
    print("\n--- Test 2: 3 Quick Requests (no delay) ---")
    quick_results = []
    for i in range(3):
        result = test_chat(token, "Create a quick task", i)
        quick_results.append(result)
        status_icon = "[OK]" if result["success"] else "[FAIL]"
        fallback_icon = "[FALLBACK]" if result["is_fallback"] else ""
        print(f"  Request {i+1}: {status_icon} {result['status']} {fallback_icon}")

    # Summary
    print("\n--- Summary ---")
    total = len(results) + len(quick_results)
    successes = sum(1 for r in results + quick_results if r["success"])
    fallbacks = sum(1 for r in results + quick_results if r["is_fallback"])
    tool_calls = sum(1 for r in results + quick_results if r["has_tool_calls"])

    print(f"Total requests: {total}")
    print(f"Successful: {successes}")
    print(f"Fallback mode: {fallbacks}")
    print(f"With tool calls: {tool_calls}")

    if fallbacks > 0:
        print("\n[!] WARNING: Some requests triggered fallback mode!")
        print("This indicates Groq API is failing or rate limiting.")
    else:
        print("\n[OK] All requests succeeded with proper AI responses!")

if __name__ == "__main__":
    main()
