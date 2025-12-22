"""Test Gemini API directly to debug connection issues."""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_gemini_direct():
    """Test calling Gemini API directly."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

    print(f"API Key: {api_key[:20]}..." if api_key else "No API key")
    print(f"Base URL: {base_url}")

    # Test direct httpx call with native Gemini API
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    data = {
        "contents": [{
            "parts": [{
                "text": "Hello, can you help me?"
            }]
        }]
    }

    print(f"\nMaking request to native Gemini API...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=data,
                params={"key": api_key},
                timeout=30.0
            )

            print(f"\nResponse status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            if response.status_code == 200:
                result = response.json()
                print(f"\nSuccess! Response: {result}")
            else:
                print(f"\nError response: {response.text}")

        except Exception as e:
            print(f"\nException: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_direct())