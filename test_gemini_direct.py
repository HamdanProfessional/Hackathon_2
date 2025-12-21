#!/usr/bin/env python3
"""
Test script to verify Google Gemini API using Google's official library.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))
os.chdir(backend_path)

async def test_gemini_direct():
    """Test Gemini using Google's official library."""

    print("=" * 60)
    print("Testing Google Gemini API (Direct)")
    print("=" * 60)

    try:
        # Import Google's official library
        import google.generativeai as genai
        from app.config import settings

        print(f"[CONFIG] AI_API_KEY configured: {bool(settings.AI_API_KEY and settings.AI_API_KEY.strip())}")
        print(f"[CONFIG] API Key (first 10 chars): {settings.AI_API_KEY[:10] if settings.AI_API_KEY else 'None'}...")

        # Configure the API
        genai.configure(api_key=settings.AI_API_KEY)

        # Test basic generation
        print("\n[TEST] Testing basic text generation...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, please respond with 'Gemini AI is working!'")
        print(f"[SUCCESS] Response: {response.text}")

        # Test with tools
        print("\n[TEST] Testing function calling capabilities...")
        import json

        # Define a simple tool
        def add_task(title: str, description: str = None):
            """Mock function to add a task."""
            return {"status": "success", "task_id": 123, "title": title, "description": description}

        # Test function calling
        model_with_tools = genai.GenerativeModel(
            'gemini-1.5-flash',
            tools=[{
                "function_declarations": [{
                    "name": "add_task",
                    "description": "Add a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Task title"},
                            "description": {"type": "string", "description": "Task description"}
                        },
                        "required": ["title"]
                    }
                }]
            }]
        )

        response = model_with_tools.generate_content("Please create a task called 'Test task from Gemini'")

        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            print(f"[SUCCESS] Function call: {function_call.name}")
            print(f"[INFO] Arguments: {function_call.args}")
        else:
            print(f"[INFO] No function call, response: {response.text}")

        print("\n" + "=" * 60)
        print("[SUCCESS] Gemini API is working!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
        print("[FAILED] Gemini API test failed!")
        print("=" * 60)
        return False

    return True

if __name__ == "__main__":
    result = asyncio.run(test_gemini_direct())
    sys.exit(0 if result else 1)