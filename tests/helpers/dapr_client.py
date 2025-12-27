"""
Dapr Test Helper Client

Mock and real Dapr client for testing event publishing in Phase V.
Supports both mock mode (for unit tests) and real mode (for integration tests).
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import httpx

logger = logging.getLogger(__name__)


class MockDaprClient:
    """
    Mock Dapr client for testing without a real Dapr sidecar.

    Stores published events in memory for verification in tests.
    """

    def __init__(self):
        """Initialize mock Dapr client with event storage."""
        self.published_events: List[Dict[str, Any]] = []
        self.enabled = True
        self.should_fail = False
        self.fail_on_topics: List[str] = []

    def reset(self):
        """Clear all stored events."""
        self.published_events.clear()

    def enable_failure(self, topic: Optional[str] = None):
        """
        Enable failure mode.

        Args:
            topic: If specified, only fail on this topic. Otherwise fail all.
        """
        self.should_fail = True
        if topic:
            self.fail_on_topics.append(topic)

    def disable_failure(self):
        """Disable failure mode."""
        self.should_fail = False
        self.fail_on_topics.clear()

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Mock publish event to Dapr.

        Args:
            pubsub_name: Pub/sub component name
            topic: Event topic name
            data: Event payload

        Returns:
            True if published successfully, False if in failure mode
        """
        if not self.enabled:
            logger.debug(f"Mock Dapr client disabled. Skipping event: {topic}")
            return False

        # Check if this topic should fail
        if self.should_fail and (not self.fail_on_topics or topic in self.fail_on_topics):
            logger.warning(f"Mock Dapr client failing on topic: {topic}")
            return False

        # Store event for verification
        event_record = {
            "pubsub_name": pubsub_name,
            "topic": topic,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.published_events.append(event_record)

        logger.info(f"Mock Dapr: Event published to topic '{topic}': {data.get('task_id', 'N/A')}")
        return True

    def get_events_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all events published to a specific topic.

        Args:
            topic: Topic name to filter by

        Returns:
            List of events published to the topic
        """
        return [e for e in self.published_events if e["topic"] == topic]

    def get_events_by_task_id(self, task_id: int) -> List[Dict[str, Any]]:
        """
        Get all events for a specific task.

        Args:
            task_id: Task ID to filter by

        Returns:
            List of events for the task
        """
        return [
            e for e in self.published_events
            if e["data"].get("task_id") == task_id
        ]

    def verify_event_published(
        self,
        topic: str,
        task_id: Optional[int] = None,
        event_type: Optional[str] = None
    ) -> bool:
        """
        Verify that an event was published.

        Args:
            topic: Topic to check
            task_id: Optional task ID to verify
            event_type: Optional event type to verify in data

        Returns:
            True if matching event found
        """
        events = self.get_events_by_topic(topic)

        if task_id is not None:
            events = [e for e in events if e["data"].get("task_id") == task_id]

        if event_type is not None:
            events = [e for e in events if e["data"].get("event_type") == event_type]

        return len(events) > 0

    def get_event_count(self, topic: Optional[str] = None) -> int:
        """
        Get count of published events.

        Args:
            topic: Optional topic to filter by

        Returns:
            Number of events
        """
        if topic:
            return len(self.get_events_by_topic(topic))
        return len(self.published_events)


class RealDaprClient:
    """
    Real Dapr client for integration testing with actual Dapr sidecar.

    This client communicates with the real Dapr sidecar via HTTP.
    """

    def __init__(
        self,
        dapr_host: str = "localhost",
        dapr_port: str = "3500",
        pubsub_name: str = "todo-pubsub"
    ):
        """
        Initialize real Dapr client.

        Args:
            dapr_host: Dapr sidecar host
            dapr_port: Dapr sidecar HTTP port
            pubsub_name: Pub/sub component name
        """
        self.dapr_host = dapr_host
        self.dapr_port = dapr_port
        self.pubsub_name = pubsub_name
        self.base_url = f"http://{dapr_host}:{dapr_port}/v1.0"
        self.enabled = os.getenv("DAPR_ENABLED", "true").lower() == "true"

    def _get_publish_url(self, topic: str) -> str:
        """Build Dapr publish URL for a topic."""
        return f"{self.base_url}/publish/{self.pubsub_name}/{topic}"

    async def publish_event(
        self,
        pubsub_name: str,
        topic: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Publish event to real Dapr sidecar.

        Args:
            pubsub_name: Pub/sub component name
            topic: Event topic name
            data: Event payload

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr disabled. Skipping event: {topic}")
            return False

        url = self._get_publish_url(topic)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json=data)

                if response.status_code == 200:
                    logger.info(f"Real Dapr: Event published to topic '{topic}'")
                    return True
                else:
                    logger.error(
                        f"Real Dapr: Failed to publish event to topic '{topic}': "
                        f"status={response.status_code}"
                    )
                    return False

        except httpx.ConnectError:
            logger.warning(
                f"Real Dapr: Sidecar not available at {self.dapr_host}:{self.dapr_port}"
            )
            return False
        except Exception as e:
            logger.error(f"Real Dapr: Error publishing event: {e}")
            return False

    async def health_check(self) -> bool:
        """
        Check if Dapr sidecar is healthy.

        Returns:
            True if Dapr is responding
        """
        try:
            health_url = f"{self.base_url}/healthz"
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(health_url)
                return response.status_code == 200
        except Exception:
            return False

    async def get_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Get all registered Dapr subscriptions.

        Returns:
            List of subscription configurations
        """
        try:
            subscriptions_url = f"{self.base_url}/subscriptions"
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(subscriptions_url)
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception as e:
            logger.error(f"Error getting subscriptions: {e}")
            return []


def get_dapr_client(
    use_real: bool = False,
    **kwargs
) -> Optional[MockDaprClient | RealDaprClient]:
    """
    Factory function to get appropriate Dapr client.

    Args:
        use_real: If True, return RealDaprClient. Otherwise MockDaprClient.
        **kwargs: Additional arguments passed to client constructor

    Returns:
        Dapr client instance
    """
    if use_real:
        return RealDaprClient(**kwargs)
    return MockDaprClient(**kwargs)
