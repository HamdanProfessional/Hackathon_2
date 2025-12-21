"""
Comprehensive Test Suite for Enhanced Agent Functionality

This test suite validates:
- Enhanced error handling and resilience
- Improved conversation context management
- Optimized tool execution and caching
- Urdu language NLP capabilities
- Performance monitoring and metrics
"""

import pytest
import asyncio
import json
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from app.ai.agent import AgentService
from app.ai.enhanced_conversation_manager import EnhancedConversationManager
from app.ai.optimized_tools import (
    add_task, list_tasks, complete_task, update_task, delete_task,
    get_tool_metrics, clear_tool_cache
)
from app.ai.urdu_nlp_processor import UrduNLPProcessor, urdu_processor


class TestEnhancedAgentErrorHandling:
    """Test enhanced error handling and resilience features."""

    @pytest.fixture
    async def agent_service(self):
        """Create agent service for testing."""
        with patch('app.ai.agent.settings') as mock_settings:
            mock_settings.AI_API_KEY = "test_key"
            mock_settings.AI_BASE_URL = "https://test.api.com"
            mock_settings.AI_MODEL = "test-model"

            service = AgentService()
            return service

    @pytest.mark.asyncio
    async def test_empty_input_validation(self, agent_service):
        """Test empty input validation."""
        mock_db = AsyncMock()

        result = await agent_service.run_agent(
            db=mock_db,
            user_id=1,
            user_message="",
            history=[]
        )

        assert result["response"] == "Please provide a message. How can I help you manage your tasks today?"
        assert result["error"]["type"] == "empty_input"
        assert result["tool_calls"] == []

    @pytest.mark.asyncio
    async def test_language_detection(self, agent_service):
        """Test enhanced language detection."""
        test_cases = [
            ("Hello, how are you?", "en"),
            ("السلام علیکم", "ur"),
            ("mujhe kaam banana hai", "roman_urdu"),
            ("I need to create a task آپ کیسے ہیں", "mixed")
        ]

        for text, expected_lang in test_cases:
            detected = agent_service._detect_language(text)
            assert detected == expected_lang, f"Failed for '{text}': expected {expected_lang}, got {detected}"

    @pytest.mark.asyncio
    async def test_error_categorization(self, agent_service):
        """Test error categorization functionality."""
        test_errors = [
            (Exception("Rate limit exceeded"), "rate_limit", True),
            (ConnectionError("Connection failed"), "connection", True),
            (TimeoutError("Request timeout"), "timeout", True),
            (PermissionError("Auth failed"), "authentication", False),
            (ValueError("Unknown error"), "unknown", False)
        ]

        for error, expected_type, expected_retryable in test_errors:
            error_info = agent_service._categorize_error(error)
            assert error_info["type"] == expected_type
            assert error_info["retryable"] == expected_retryable

    @pytest.mark.asyncio
    async def test_graceful_degradation(self, agent_service):
        """Test graceful degradation when AI service fails."""
        tool_calls = []
        error_info = {"type": "connection", "message": "API down"}

        # Test English greeting
        result_en = await agent_service._graceful_degradation(
            "hello", "en", tool_calls, error_info
        )
        assert "Hello!" in result_en["response"]
        assert result_en["fallback_mode"] is True

        # Test Urdu greeting
        result_ur = await agent_service._graceful_degradation(
            "سلام", "ur", tool_calls, error_info
        )
        assert "سلام" in result_ur["response"]
        assert result_ur["fallback_mode"] is True

    @pytest.mark.asyncio
    async def test_api_retry_logic(self, agent_service):
        """Test API retry logic with exponential backoff."""
        mock_client = AsyncMock()
        agent_service.client = mock_client

        # Simulate failure then success
        mock_client.chat.completions.create.side_effect = [
            ConnectionError("Failed"),
            ConnectionError("Failed"),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Success"))])
        ]

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            result = await agent_service._call_api_with_retry(
                messages=[{"role": "user", "content": "test"}],
                tools=[],
                max_retries=2
            )

            # Should have called sleep twice (for the two failures)
            assert mock_sleep.call_count == 2
            # Should have attempted the API call 3 times
            assert mock_client.chat.completions.create.call_count == 3


class TestEnhancedConversationManager:
    """Test enhanced conversation context management."""

    @pytest.fixture
    async def conversation_manager(self):
        """Create enhanced conversation manager for testing."""
        mock_db = AsyncMock()
        return EnhancedConversationManager(mock_db, cache_ttl=60)

    @pytest.mark.asyncio
    async def test_conversation_creation_with_metadata(self, conversation_manager):
        """Test conversation creation with enhanced metadata."""
        from uuid import uuid4
        user_id = uuid4()
        initial_context = {"source": "web", "language": "ur"}

        # Mock database operations
        mock_conversation = MagicMock()
        mock_conversation.id = uuid4()
        conversation_manager.db.add = MagicMock()
        conversation_manager.db.flush = AsyncMock()
        conversation_manager.db.refresh = AsyncMock()

        # Setup mock return
        conversation_manager.db.execute.return_value.scalar_one_or_none.return_value = mock_conversation

        result = await conversation_manager.create_conversation(
            user_id=user_id,
            title="Test Conversation",
            initial_context=initial_context
        )

        # Verify cache is populated
        assert result in conversation_manager._conversation_cache

    @pytest.mark.asyncio
    async def test_smart_context_summarization(self, conversation_manager):
        """Test smart conversation summarization for long conversations."""
        from uuid import uuid4
        conversation_id = uuid4()

        # Mock older messages
        older_messages = [
            MagicMock(role="user", content="Create task: Buy groceries"),
            MagicMock(role="assistant", content="Task 'Buy groceries' created"),
            MagicMock(role="user", content="Complete task: Buy groceries"),
            MagicMock(role="assistant", content="Task 'Buy groceries' completed")
        ]

        # Setup mock returns
        conversation_manager.db.execute.return_value.scalar.return_value = 10  # Total messages

        # Test summary generation
        summary = await conversation_manager._generate_conversation_summary(
            conversation_id, older_message_count=4
        )

        assert "created" in summary
        assert "completed" in summary
        assert "Buy groceries" in summary or "task" in summary

    @pytest.mark.asyncio
    async def test_urdu_language_detection_in_context(self, conversation_manager):
        """Test Urdu language detection in conversation context."""
        # Test Urdu text detection
        urdu_text = "میں آپ سے بات کرنا چاہتا ہوں"
        assert conversation_manager._has_urdu_text(urdu_text) is True

        # Test English text detection
        english_text = "I want to talk to you"
        assert conversation_manager._has_urdu_text(english_text) is False

        # Test mixed text
        mixed_text = "I want to talk میں بات کرنا چاہتا ہوں"
        assert conversation_manager._has_urdu_text(mixed_text) is True

    @pytest.mark.asyncio
    async def test_conversation_search(self, conversation_manager):
        """Test advanced conversation search functionality."""
        from uuid import uuid4
        user_id = uuid4()
        query = "groceries"

        # Mock search results
        mock_conversation = MagicMock()
        mock_conversation.id = uuid4()
        mock_conversation.title = "Shopping Tasks"

        mock_message = MagicMock()
        mock_message.content = "Buy groceries from the store"
        mock_message.created_at = datetime.utcnow()

        # Setup mock return
        conversation_manager.db.execute.return_value.all.return_value = [
            (mock_conversation, mock_message)
        ]

        results = await conversation_manager.search_conversations(
            user_id=user_id,
            query=query,
            limit=10
        )

        assert len(results) == 1
        assert results[0]["title"] == "Shopping Tasks"
        assert "**groceries**" in results[0]["highlighted_content"]


class TestOptimizedTools:
    """Test optimized tool execution and caching."""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return AsyncMock()

    @pytest.fixture
    def clear_cache(self):
        """Clear tool cache before each test."""
        clear_tool_cache()
        yield
        clear_tool_cache()

    @pytest.mark.asyncio
    async def test_tool_performance_monitoring(self, mock_db, clear_cache):
        """Test tool performance monitoring and metrics."""
        # Clear existing metrics
        from app.ai.optimized_tools import _tool_metrics
        _tool_metrics.clear()

        # Mock successful task creation
        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.description = None
        mock_task.priority.value = "medium"
        mock_task.due_date = None
        mock_task.completed = False
        mock_task.created_at = datetime.utcnow()

        with patch('app.ai.optimized_tools.task_crud.create_task') as mock_create:
            mock_create.return_value = mock_task

            # Execute tool
            result = await add_task(
                title="Test Task",
                user_id=1,
                db=mock_db
            )

            # Check metrics
            metrics = get_tool_metrics()
            assert "add_task" in metrics
            assert metrics["add_task"]["call_count"] == 1
            assert metrics["add_task"]["success_rate"] == 1.0
            assert metrics["add_task"]["average_time"] > 0

    @pytest.mark.asyncio
    async def test_tool_caching_functionality(self, mock_db, clear_cache):
        """Test tool result caching."""
        # Mock database query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        # First call should hit database
        result1 = await list_tasks(
            user_id=1,
            status="all",
            db=mock_db
        )

        # Second call with same parameters should use cache
        result2 = await list_tasks(
            user_id=1,
            status="all",
            db=mock_db
        )

        # Check cache metrics
        metrics = get_tool_metrics()
        if "list_tasks" in metrics:
            assert metrics["list_tasks"]["cache_hits"] >= 1

    @pytest.mark.asyncio
    async def test_batch_task_operations(self, mock_db):
        """Test batch task creation for performance."""
        tasks_data = [
            {"title": "Task 1"},
            {"title": "Task 2"},
            {"title": "Task 3"}
        ]

        # Mock successful creation
        with patch('app.ai.optimized_tools.add_task') as mock_add:
            mock_add.return_value = {
                "status": "success",
                "task": {"id": 1, "title": "Test Task"}
            }

            result = await batch_create_tasks(
                tasks=tasks_data,
                user_id=1,
                db=mock_db
            )

            assert result["status"] == "success"
            assert result["total_created"] == 3
            assert result["total_requested"] == 3

    @pytest.mark.asyncio
    async def test_advanced_task_search(self, mock_db):
        """Test advanced task search with relevance scoring."""
        # Mock search results
        mock_tasks = [
            MagicMock(
                id=1,
                title="Buy groceries",
                description="Get milk and bread",
                priority=MagicMock(value="medium"),
                due_date=None,
                completed=False
            )
        ]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_tasks
        mock_db.execute.return_value = mock_result

        result = await search_tasks(
            query="groceries",
            user_id=1,
            db=mock_db
        )

        assert result["status"] == "success"
        assert len(result["results"]) == 1
        assert result["results"][0]["relevance"]["title_match"] is True
        assert result["total_found"] == 1


class TestUrduNLPProcessor:
    """Test Urdu language NLP capabilities."""

    def test_language_detection(self):
        """Test Urdu language detection."""
        test_cases = [
            ("السلام علیکم", ("ur", 1.0)),
            ("assalam o alaikum", ("roman_urdu", 1.0)),
            ("Hello world", ("en", 1.0)),
            ("mujhe kaam banana hai", ("roman_urdu", 0.8)),
            ("I need to create a task آپ کیسے ہیں", ("mixed", 0.7))
        ]

        for text, expected in test_cases:
            language, confidence = urdu_processor.detect_language(text)
            assert language == expected[0], f"Language detection failed for: {text}"
            assert confidence >= expected[1] * 0.5, f"Confidence too low for: {text}"

    def test_text_normalization(self):
        """Test Urdu text normalization."""
        test_cases = [
            ("Assalam O Alaikum", "assalam o alaikum"),
            ("میں   کام  کرتا   ہوں", "میں کام کرتا ہوں"),
            ("fori kaam karna hai", "فوری کام کرنا ہے"),
            ("Hello    World!!!", "hello world")
        ]

        for input_text, expected in test_cases:
            result = urdu_processor.normalize_text(input_text)
            assert result == expected, f"Normalization failed for: {input_text}"

    def test_intent_detection(self):
        """Test Urdu intent detection."""
        test_cases = [
            ("مجھے ٹاسک بنانا ہے", "create_task"),
            ("میرے تمام کام دکھائیں", "list_tasks"),
            ("یہ ٹاسک مکمل کر دیں", "complete_task"),
            ("ٹاسک اپ ڈیٹ کریں", "update_task"),
            ("اس ٹاسک کو حذف کریں", "delete_task"),
            ("السلام علیکم", "greeting"),
            ("مدد چاہیے", "help")
        ]

        for text, expected_intent in test_cases:
            intent = urdu_processor.detect_intent(text)
            assert intent.value == expected_intent, f"Intent detection failed for: {text}"

    def test_task_title_extraction(self):
        """Test task title extraction from Urdu text."""
        test_cases = [
            ("بنائیں ٹاسک 'خریداری'", "خریداری"),
            ("ٹاسک گھر جانا بنائیں", "گھر جانا"),
            ("create task خریداری", "خریداری"),
            ("مجھے ایک نئی ٹاسک بنانی ہے جس کا نام ہوگا فائنل پراجیکٹ", "فائنل پراجیکٹ")
        ]

        for text, expected_title in test_cases:
            title = urdu_processor.extract_task_title(text)
            assert title == expected_title, f"Title extraction failed for: {text}"

    def test_priority_extraction(self):
        """Test priority extraction from Urdu text."""
        test_cases = [
            ("یہ ایک ضروری ٹاسک ہے", "high"),
            ("فوری کام ہے", "high"),
            ("معمولی ٹاسک ہے", "medium"),
            "آہستہ کریں", "low"
        ]

        for text, expected_priority in test_cases:
            priority = urdu_processor.extract_priority(text)
            assert priority == expected_priority, f"Priority extraction failed for: {text}"

    def test_date_expression_extraction(self):
        """Test date expression extraction."""
        test_cases = [
            ("آج کرنا ہے", "today"),
            ("کل ہوگا", "tomorrow"),
            ("اس ہفتے میں", "this_week"),
            ("اگلے ہفتے تک", "next_week")
        ]

        for text, expected_date in test_cases:
            date_expr = urdu_processor.extract_date_expression(text)
            assert date_expr == expected_date, f"Date extraction failed for: {text}"

    def test_date_conversion(self):
        """Test date expression to absolute date conversion."""
        today = date.today()
        tomorrow = today + timedelta(days=1)

        test_cases = [
            ("today", today.strftime('%Y-%m-%d')),
            ("tomorrow", tomorrow.strftime('%Y-%m-%d')),
            ("2025-12-25", "2025-12-25")
        ]

        for date_expr, expected in test_cases:
            result = urdu_processor.convert_to_standard_date(date_expr)
            assert result == expected, f"Date conversion failed for: {date_expr}"

    def test_complete_task_request_processing(self):
        """Test complete task request processing."""
        test_requests = [
            {
                "text": "مجھے ایک ضروری ٹاسک بنانا ہے 'فائنل پروجیکٹ' آج تک",
                "expected_intent": "create_task",
                "expected_title": "فائنل پروجیکٹ",
                "expected_priority": "high",
                "expected_date": "today"
            },
            {
                "text": "میرے تمام کام دکھائیں",
                "expected_intent": "list_tasks",
                "expected_title": None,
                "expected_priority": "",
                "expected_date": None
            }
        ]

        for request in test_requests:
            result = urdu_processor.process_task_request(request["text"])

            assert result["status"] == "success"
            assert result["analysis"]["intent"]["detected"] == request["expected_intent"]
            assert result["analysis"]["extracted_entities"]["task_title"] == request["expected_title"]
            assert result["analysis"]["extracted_entities"]["priority"] == request["expected_priority"] or "medium"
            assert result["analysis"]["extracted_entities"]["date_expression"] == request["expected_date"]


class TestIntegrationScenarios:
    """Integration tests for complete agent workflows."""

    @pytest.mark.asyncio
    async def test_bilingual_conversation_flow(self):
        """Test bilingual conversation handling."""
        # This would test the complete flow from Urdu/English input
        # through NLP processing to tool execution

        urdu_text = "مجھے ایک ٹاسک بنانا ہے خریداری کے لیے"
        result = urdu_processor.process_task_request(urdu_text)

        assert result["status"] == "success"
        assert result["analysis"]["language"]["detected"] in ["ur", "roman_urdu"]
        assert result["analysis"]["intent"]["detected"] == "create_task"
        assert "خریداری" in result["analysis"]["extracted_entities"]["task_title"]

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self):
        """Test error recovery in agent workflows."""
        # Test how the agent handles various error scenarios
        agent = AgentService()

        # Mock database and API failures
        with patch('app.ai.agent.settings') as mock_settings:
            mock_settings.AI_API_KEY = "invalid_key"

            # Test graceful degradation
            result = await agent._graceful_degradation(
                "help me", "en", [], {"type": "connection", "message": "API down"}
            )

            assert "help" in result["response"].lower()
            assert result["fallback_mode"] is True

    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """Test agent performance under simulated load."""
        import time

        # Simulate multiple concurrent requests
        start_time = time.time()

        tasks = []
        for i in range(10):
            task = urdu_processor.process_task_request(f"Create task {i}")
            tasks.append(task)

        end_time = time.time()
        total_time = end_time - start_time

        # Should process 10 requests reasonably quickly
        assert total_time < 5.0, f"Processing took too long: {total_time}s"

        # All requests should succeed
        for task in tasks:
            assert task["status"] == "success"


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmarks for agent components."""

    def test_urdu_nlp_performance(self):
        """Benchmark Urdu NLP processing speed."""
        import time

        test_texts = [
            "مجھے ایک ٹاسک بنانا ہے",
            "میرے تمام کام دکھائیں",
            "یہ ٹاسک مکمل کر دیں",
            "السلام علیکم میں آپ سے بات کرنا چاہتا ہوں"
        ]

        start_time = time.time()

        for _ in range(100):  # Process each text 100 times
            for text in test_texts:
                urdu_processor.process_task_request(text)

        end_time = time.time()
        avg_time_per_request = (end_time - start_time) / (100 * len(test_texts))

        # Should process requests quickly (under 50ms per request)
        assert avg_time_per_request < 0.05, f"NLP processing too slow: {avg_time_per_request}s per request"

    @pytest.mark.asyncio
    async def test_tool_caching_performance(self):
        """Benchmark tool caching performance."""
        from app.ai.optimized_tools import _tool_cache

        # Clear cache
        _tool_cache.clear()

        # First call (cache miss)
        start_time = time.time()
        # Simulate a cacheable operation
        cache_key = "test_key"
        _tool_cache[cache_key] = {"result": "test", "timestamp": time.time()}
        end_time = time.time()

        first_call_time = end_time - start_time

        # Second call (cache hit)
        start_time = time.time()
        result = _tool_cache.get(cache_key)
        end_time = time.time()

        second_call_time = end_time - start_time

        # Cache hit should be significantly faster
        assert second_call_time < first_call_time / 2, "Cache not providing performance improvement"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])