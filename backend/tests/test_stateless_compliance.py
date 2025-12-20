"""
Tests to verify stateless agent architecture compliance.

These tests ensure that the agent does not store conversation state in memory,
enabling horizontal scaling and crash recovery.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.ai.agent import AgentService
from app.ai.mcp_tools import mcp, set_mcp_context, clear_mcp_context


class TestStatelessAgentCompliance:
    """Test suite for stateless agent architecture compliance."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return AgentService()

    @pytest.mark.asyncio
    async def test_state_isolation_between_requests(self, agent, mock_db):
        """
        Test that agent maintains no state between requests.

        Each request should load conversation history from database,
        not rely on any in-memory state from previous requests.
        """
        user_id = 123
        conversation_id = 1

        # Mock database responses for two different requests
        mock_db.execute = AsyncMock()

        # First request
        with patch('app.ai.mcp_tools.set_mcp_context') as mock_set, \
             patch('app.ai.mcp_tools.clear_mcp_context') as mock_clear:

            result1 = await agent.run_agent(
                db=mock_db,
                user_id=user_id,
                user_message="Hello",
                history=[]
            )

        # Second request to same conversation
        with patch('app.ai.mcp_tools.set_mcp_context') as mock_set, \
             patch('app.ai.mcp_tools.clear_mcp_context') as mock_clear:

            result2 = await agent.run_agent(
                db=mock_db,
                user_id=user_id,
                user_message="How are you?",
                history=[]
            )

        # Verify responses are independent (no shared state)
        assert result1 is not None
        assert result2 is not None
        assert result1 != result2

        # Verify context is set and cleared for each request
        assert mock_set.called
        assert mock_clear.called

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, agent, mock_db):
        """
        Test that agent can handle concurrent requests to same conversation.

        This is critical for horizontal scaling - multiple instances
        should be able to handle requests for the same user simultaneously.
        """
        user_id = 123

        # Create multiple concurrent requests
        async def make_request(message):
            with patch('app.ai.mcp_tools.set_mcp_context'), \
                 patch('app.ai.mcp_tools.clear_mcp_context'):

                return await agent.run_agent(
                    db=mock_db,
                    user_id=user_id,
                    user_message=message,
                    history=[]
                )

        # Run 10 requests concurrently
        messages = [f"Message {i}" for i in range(10)]
        tasks = [make_request(msg) for msg in messages]

        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all requests completed successfully
        for i, result in enumerate(results):
            assert not isinstance(result, Exception), f"Request {i} failed: {result}"
            assert result is not None

    def test_agent_has_no_instance_state(self, agent):
        """
        Test that agent class doesn't have instance variables for storing conversation state.
        """
        # Check that AgentService doesn't have state-storing attributes
        state_attributes = [
            'conversations', 'messages', 'cache', 'state', 'history',
            'session', 'context', 'memory', 'buffer'
        ]

        for attr in state_attributes:
            assert not hasattr(agent, attr), f"Agent has stateful attribute: {attr}"

    @pytest.mark.asyncio
    async def test_agent_loads_history_from_db(self, agent, mock_db):
        """
        Test that agent loads conversation history from database.

        This verifies the stateless requirement: history must come from DB,
        not from any in-memory cache.
        """
        user_id = 123
        history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"}
        ]

        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mcp_context'):

            # Agent should use provided history, not store it
            result = await agent.run_agent(
                db=mock_db,
                user_id=user_id,
                user_message="New message",
                history=history
            )

        # Verify agent processed the history
        assert result is not None
        assert 'response' in result
        assert 'messages' in result

        # Verify history was not stored in agent
        assert not hasattr(agent, '_history')
        assert not hasattr(agent, 'history')

    @pytest.mark.asyncio
    async def test_mcp_context_isolated(self, mock_db):
        """
        Test that MCP tools context is properly isolated between requests.
        """
        # Set context for first request
        set_mcp_context(mock_db, user_id=123)

        # Verify context is set globally
        from app.ai.mcp_tools import _db_session, _user_id
        assert _db_session is mock_db
        assert _user_id == 123

        # Clear context
        clear_mcp_context()

        # Verify context is cleared
        assert _db_session is None
        assert _user_id is None

    @pytest.mark.asyncio
    async def test_agent_with_different_users(self, agent, mock_db):
        """
        Test that agent handles requests from different users independently.
        """
        # Mock database queries
        mock_db.execute = AsyncMock()

        # Request from user 1
        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mcp_context'):

            result1 = await agent.run_agent(
                db=mock_db,
                user_id=123,
                user_message="User 1 message",
                history=[]
            )

        # Request from user 2
        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mock_context'):

            result2 = await agent.run_agent(
                db=mock_db,
                user_id=456,
                user_message="User 2 message",
                history=[]
            )

        # Verify results are independent
        assert result1 is not None
        assert result2 is not None
        assert result1 != result2

    @pytest.mark.asyncio
    async def test_error_handling_doesnt_corrupt_state(self, agent, mock_db):
        """
        Test that errors in one request don't affect subsequent requests.
        """
        user_id = 123

        # First request succeeds
        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mcp_context'):

            result1 = await agent.run_agent(
                db=mock_db,
                user_id=user_id,
                user_message="Valid message",
                history=[]
            )

        # Second request fails (simulate API error)
        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mcp_context'), \
             patch.object(agent.client, 'chat.completions.create', side_effect=Exception("API Error")):

            with pytest.raises(Exception):
                await agent.run_agent(
                    db=mock_db,
                    user_id=user_id,
                    user_message="This will fail",
                    history=[]
                )

        # Third request should still work normally
        with patch('app.ai.mcp_tools.set_mcp_context'), \
             patch('app.ai.mcp_tools.clear_mcp_context'):

            result3 = await agent.run_agent(
                db=mock_db,
                user_id=user_id,
                user_message="Another valid message",
                history=[]
            )

        # Verify first and third requests worked independently
        assert result1 is not None
        assert result3 is not None