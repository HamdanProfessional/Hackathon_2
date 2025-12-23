"""Test Groq API directly"""
import os
from openai import OpenAI

# Use Groq API from environment variable
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    print("ERROR: GROQ_API_KEY environment variable not set")
    exit(1)

base_url = "https://api.groq.com/openai/v1"
model = "llama-3.3-70b-versatile"

print(f"Testing Groq API...")
print(f"Base URL: {base_url}")
print(f"Model: {model}")
print(f"API Key: {api_key[:20]}...")

try:
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello"}
        ]
    )

    print(f"\nSUCCESS!")
    print(f"Response: {response.choices[0].message.content}")

except Exception as e:
    print(f"\nERROR!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")

    # Check if it contains "429" or rate limit info
    if "429" in str(e):
        print("\n!! This IS a rate limit error !!")
    if "rate" in str(e).lower():
        print("\n!! Error contains 'rate' !!")
