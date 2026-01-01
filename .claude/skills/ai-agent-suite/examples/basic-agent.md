# Basic AI Agent Example

A minimal stateless AI agent with AsyncOpenAI.

## Implementation

```python
# backend/app/ai/basic_agent.py
from openai import AsyncOpenAI
from app.config import settings

class BasicAgent:
    """Minimal stateless AI agent."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL

    async def chat(self, message: str, history: list[dict]) -> str:
        """Process a chat message with conversation history."""
        messages = history + [{"role": "user", "content": message}]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content
```

## Usage

```python
# FastAPI endpoint
from fastapi import APIRouter, Depends
from app.ai.basic_agent import BasicAgent

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(message: str):
    agent = BasicAgent()
    response = await agent.chat(message, history=[])
    return {"response": response}
```

## Key Points

- **Stateless**: No instance variables storing conversation state
- **History passed in**: Conversation history fetched from DB each request
- **Async**: Uses AsyncOpenAI for non-blocking operations
- **Configurable**: Model and API endpoint from settings
