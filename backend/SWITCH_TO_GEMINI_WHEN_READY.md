# How to Switch to Gemini (When Quota Resets)

## Current Issue
Your Gemini API key has hit the free tier daily limit. You'll need to wait until the quota resets (usually midnight UTC) or upgrade to a paid plan.

## Steps to Use Gemini as Primary

### Step 1: Wait for Quota Reset
The Gemini free tier resets daily. Check your quota at:
https://aistudio.google.com/app/apikey

### Step 2: Update .env File
Comment out or remove the OpenAI key to force Gemini usage:

```env
# OpenAI API Key for AI agent (primary)
# OPENAI_API_KEY=sk-proj-...  # Commented out

# Gemini API Key for AI agent (backup)
GEMINI_API_KEY=AIzaSyBFzgeki-jEO3_TetuYu8s9PtUcgeSqBQU
```

### Step 3: Restart the Application
```bash
# Stop the server (Ctrl+C)
# Start again
uvicorn app.main:app --reload --port 8000
```

The app will automatically detect that OpenAI is not configured and use Gemini instead.

### Step 4: Verify
You should see this in the logs:
```
[OK] Using Gemini API as fallback
[AI] AI_MODEL configured: gemini-2.0-flash-exp
```

## Gemini Free Tier Limits

- **Requests per minute**: 15
- **Requests per day**: 1,500
- **Input tokens per minute**: 1 million

If you need more, upgrade at: https://ai.google.dev/pricing

## Recommendation

**Keep both keys configured** (current setup):
- OpenAI as primary (working now)
- Gemini as backup (will work when quota resets)

This gives you redundancy if one provider has issues.
