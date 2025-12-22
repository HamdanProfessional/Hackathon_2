"""Simple test to check where the error is coming from."""
import asyncio
from app.ai.agent_mock import MockAgentService
from app.ai.agent import AgentService
from app.database import get_db
from app.config import settings

async def test_mock_agent():
    """Test mock agent directly."""
    print("Testing Mock Agent...")

    # Get a database session
    async for db in get_db():
        # Test mock agent
        mock_agent = MockAgentService()
        result = await mock_agent.run_agent(
            db=db,
            user_id=1,
            user_message="Create a task called 'Test'",
            history=[]
        )
        print(f"Mock agent result: {result['response'][:100]}...")
        break

    print("\nTesting Real Agent (should show connection error)...")
    try:
        real_agent = AgentService()
        print("AgentService instantiated successfully")
    except Exception as e:
        print(f"Failed to instantiate AgentService: {e}")

if __name__ == "__main__":
    asyncio.run(test_mock_agent())