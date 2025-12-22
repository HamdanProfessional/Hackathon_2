---
id: gemini-api-refactor-001
title: Gemini API Refactor
stage: refactor
date: 2025-01-18T00:00:00Z
surface: cli
model: glm-4.6
feature: 003-ai-chatbot
branch: main
user: user
command: /sp.implement
labels: [ai, gemini, refactor, api]
links:
  spec: specs/features/003-ai-chatbot/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
- path: backend/app/config.py
  change_type: modified
  description: Updated AI configuration to use Google Gemini instead of OpenAI
- path: backend/.env.example
  change_type: modified
  description: Updated environment variables for Gemini API key and base URL
- path: backend/app/ai/agent.py
  change_type: modified
  description: Refactored to use AsyncOpenAI client with Gemini's OpenAI-compatible endpoint
- path: backend/app/api/chat.py
  change_type: modified
  description: Updated AgentService instantiation to use new configuration
tests:
- status: not_executed
  notes: Testing should be done by starting the backend server with a valid GEMINI_API_KEY
---

## Prompt

Refactor AgentService to use Google Gemini

CONTEXT:
We are switching the AI Provider from OpenAI (GPT-4o) to **Google Gemini (Flash)**.
**Goal**: Refactor `backend/app/ai/agent.py` to use the `AsyncOpenAI` client configured for Google's OpenAI-compatible endpoint.

INSTRUCTIONS:

1. **Update Configuration (`backend/app/core/config.py`)**:
   - Add/Update settings:
     - `AI_API_KEY`: Load from `GEMINI_API_KEY` (or `GOOGLE_API_KEY`).
     - `AI_BASE_URL`: Set default to `"https://generativelanguage.googleapis.com/v1beta/openai/"`.
     - `AI_MODEL`: Set default to `"gemini-2.5-flash"`.
   - Update `.env.example` to reflect these new variables.

2. **Refactor `backend/app/ai/agent.py`**:
   - **Client Init**: Initialize `AsyncOpenAI` using the new `base_url` and `api_key`.
     ```python
     self.client = AsyncOpenAI(
         api_key=settings.AI_API_KEY,
         base_url=settings.AI_BASE_URL
     )
     ```
   - **Logic**: Ensure the `run_agent` method uses `self.client.chat.completions.create`.
   - **Tool Compatibility**: Gemini supports the standard OpenAI Tool Schema, so the existing `tools.py` should work. Ensure the tool definitions are passed correctly in the `tools=[...]` parameter.

3. **Verification**:
   - Ensure the System Prompt still injects the `user_id` context.
   - Ensure the "Tool Call Loop" handles the response format correctly (Gemini's response structure via the compat layer is identical to OpenAI's).

ACTION:
Refactor the Agent Service to run on Google Gemini 2.0 Flash.

## Response snapshot

Successfully refactored the AgentService from OpenAI to Google Gemini:

1. **Configuration Updates**:
   - Modified `backend/app/config.py` to use `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL`
   - Updated validator to accept Gemini API keys (not prefixed with "sk-")
   - Added custom initialization to load from `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variables

2. **Environment Variables**:
   - Updated `backend/.env.example` with new Gemini configuration
   - Changed from `OPENAI_API_KEY` to `GEMINI_API_KEY`
   - Added `AI_BASE_URL` pointing to Google's OpenAI-compatible endpoint

3. **Agent Service Refactoring**:
   - Updated import from `OpenAI` to `AsyncOpenAI`
   - Modified constructor to use `settings.AI_API_KEY` and `settings.AI_BASE_URL`
   - Removed API key and model parameters from constructor (uses global settings)
   - Updated module and class docstrings to reflect Google Gemini usage

4. **Chat Endpoint Update**:
   - Simplified `AgentService` instantiation in `chat.py` (no parameters needed)

## Outcome

- ✅ Impact: Successfully migrated from OpenAI GPT-4o to Google Gemini 2.0 Flash
- 🧪 Tests: Not executed - requires backend restart with valid GEMINI_API_KEY
- 📁 Files: Modified 4 files (config.py, .env.example, agent.py, chat.py)
- 🔁 Next prompts: Test the chat functionality with a valid Gemini API key
- 🧠 Reflection: The refactor was straightforward due to Gemini's OpenAI-compatible API. No changes were needed to the tool definitions or execution logic.

## Evaluation notes (flywheel)

- Failure modes observed: None during the refactor
- Graders run and results (PASS/FAIL): Not executed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify that all tool calling functionality works correctly with Gemini's function calling implementation