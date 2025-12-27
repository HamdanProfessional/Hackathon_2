"""Dapr event publishing service for Phase V event-driven architecture."""
import os
import logging
from typing import Dict, Any, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class DaprEventPublisher:
    """
    Service for publishing events to Dapr sidecar.

    This service handles publishing task lifecycle events to Kafka/Redpanda
    through Dapr pub/sub component for Phase V event-driven architecture.
    """

    def __init__(self):
        """Initialize Dapr client configuration."""
        self.dapr_host = os.getenv("DAPR_HTTP_HOST", "localhost")
        self.dapr_port = os.getenv("DAPR_HTTP_PORT", "3500")
        self.pubsub_name = os.getenv("DAPR_PUBSUB_NAME", "todo-pubsub")
        self.enabled = os.getenv("DAPR_ENABLED", "true").lower() == "true"

    def _get_dapr_url(self, topic: str) -> str:
        """Build Dapr publish URL for a topic."""
        return f"http://{self.dapr_host}:{self.dapr_port}/v1.0/publish/{self.pubsub_name}/{topic}"

    async def publish_event(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        Publish event to Dapr pub/sub component.

        Args:
            topic: Event topic name (e.g., "task-created", "task-updated")
            data: Event payload data

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Dapr event publishing disabled. Skipping event: {topic}")
            return False

        # Add timestamp to all events
        data["timestamp"] = datetime.utcnow().isoformat()

        url = self._get_dapr_url(topic)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json=data)

                if response.status_code == 200:
                    logger.info(f"Event published successfully to topic '{topic}': {data.get('task_id', 'N/A')}")
                    return True
                else:
                    logger.error(
                        f"Failed to publish event to topic '{topic}': "
                        f"status={response.status_code}, body={response.text}"
                    )
                    return False

        except httpx.ConnectError:
            # Dapr sidecar not available - log but don't fail the request
            logger.warning(
                f"Dapr sidecar not available at {self.dapr_host}:{self.dapr_port}. "
                f"Event publishing skipped for topic '{topic}'. "
                f"This is expected in development without Dapr."
            )
            return False
        except httpx.TimeoutException:
            logger.error(f"Timeout publishing event to topic '{topic}'")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event to topic '{topic}': {e}")
            return False

    async def publish_task_created(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish task-created event.

        Event payload includes:
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - description: str
        - priority_id: int
        - due_date: Optional[str] (ISO format date)
        - completed: bool
        - is_recurring: bool
        - recurrence_pattern: Optional[str]
        - created_at: str (ISO format datetime)
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("task-created", task_data)

    async def publish_task_updated(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish task-updated event.

        Event payload includes all task fields plus:
        - updated_at: str (ISO format datetime)
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("task-updated", task_data)

    async def publish_task_completed(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish task-completed event.

        Event payload includes:
        - task_id: int
        - user_id: str (UUID)
        - completed: bool (always True)
        - completed_at: str (ISO format datetime)
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("task-completed", task_data)

    async def publish_task_deleted(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish task-deleted event.

        Event payload includes:
        - task_id: int
        - user_id: str (UUID)
        - deleted_at: str (ISO format datetime)
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("task-deleted", task_data)

    async def publish_task_due_soon(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish task-due-soon event.

        Event payload includes:
        - task_id: int
        - user_id: str (UUID)
        - title: str
        - due_date: str (ISO format date)
        - hours_until_due: int
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("task-due-soon", task_data)

    async def publish_recurring_task_due(self, task_data: Dict[str, Any]) -> bool:
        """
        Publish recurring-task-due event.

        Event payload includes:
        - recurring_task_id: int
        - user_id: str (UUID)
        - title: str
        - next_due_at: str (ISO format date)
        - recurrence_pattern: str
        - timestamp: str (ISO format datetime)
        """
        return await self.publish_event("recurring-task-due", task_data)


# Global singleton instance
dapr_event_publisher = DaprEventPublisher()
