# How to Use Gemini API

## ✅ Good News: Gemini is Working!

Your Gemini API key (`AIzaSyBFzgeki-jEO3_TetuYu8s9PtUcgeSqBQU`) is working perfectly!

### Test Results:
- ✅ Simple chat responses
- ✅ Task management queries
- ✅ Tool calling support
- ⏸️ Rate limit: 5 requests/min on free tier

## Current Configuration

Your app is configured to use **OpenAI as primary**, **Gemini as backup**:

```env
OPENAI_API_KEY=sk-proj-...  # Primary (currently active)
GEMINI_API_KEY=AIzaSyBFzgeki-jEO3_TetuYu8s9PtUcgeSqBQU  # Backup
```

## Option 1: Keep Using OpenAI (Recommended)

**No action needed!** Your app is already working with OpenAI.

- ✅ Higher rate limits
- ✅ More reliable
- ✅ Already configured and working

## Option 2: Switch to Gemini

If you want to use Gemini as the primary provider:

### Step 1: Update .env

Comment out the OpenAI key:

```env
# OpenAI API Key for AI agent (primary)
# OPENAI_API_KEY=sk-proj-...  ← Comment this out

# Gemini API Key for AI agent (backup)
GEMINI_API_KEY=AIzaSyBFzgeki-jEO3_TetuYu8s9PtUcgeSqBQU  ← Now primary
```

### Step 2: Restart the Server

```bash
# Stop the server (Ctrl+C)
# Start again
uvicorn app.main:app --reload --port 8000
```

### Step 3: Verify

You should see in the startup logs:
```
[OK] Using Gemini API as fallback
[AI] AI_MODEL configured: gemini-2.5-flash
```

## Gemini Rate Limits (Free Tier)

Be aware of these limits:
- **Requests per minute**: 5 requests (for gemini-2.5-flash)
- **Requests per day**: 1,500
- **Input tokens per minute**: 1 million

If you hit the limit, you'll see:
```
Error 429: You exceeded your current quota
Please retry in XX seconds
```

Just wait 60 seconds before trying again.

## Upgrade to Paid (If Needed)

If you need higher limits:
1. Visit: https://ai.google.dev/pricing
2. Enable billing in Google Cloud Console
3. Get higher quotas (up to 1,000 requests/min)

## Recommendation

**Keep your current setup** (OpenAI primary + Gemini backup):
- Redundancy: If one fails, the other works
- Best of both worlds
- No single point of failure

Only switch to Gemini-only if you specifically need Gemini's features or pricing.

## Configuration Summary

### Current Setup (Working):
```
Provider: OpenAI
Model: gpt-4o-mini
Status: ✅ Active
Rate Limit: Higher (varies by plan)
```

### Gemini Setup (Ready to Use):
```
Provider: Google Gemini
Model: gemini-2.5-flash
Status: ✅ Tested and working
Rate Limit: 5 requests/min (free tier)
Base URL: https://generativelanguage.googleapis.com/v1beta/openai/
```

## Troubleshooting

### "Rate limit exceeded"
- Wait 60 seconds
- Or upgrade to paid tier

### "Model not found"
- Ensure model name is: `gemini-2.5-flash` (not `models/gemini-2.5-flash`)
- Check base URL is correct

### "Authentication error"
- Verify API key in .env
- Ensure no extra spaces or quotes

## Testing

To verify Gemini is working, check the chat functionality:
1. Navigate to your chat interface
2. Send a message: "Hello, create a task to test Gemini"
3. You should get a response from Gemini

The agent will automatically use tool calling to create tasks!
