"""Dapr event publishing service for Phase V event-driven architecture."""
import os
import sys
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
        print(f"[DAPR-PUB] Enabled: {self.enabled}, Topic: {topic}", file=sys.stderr)
        if not self.enabled:
            print(f"[DAPR-PUB] Dapr event publishing disabled. Skipping event: {topic}", file=sys.stderr)
            return False

        # Add timestamp to all events
        data["timestamp"] = datetime.utcnow().isoformat()

        url = self._get_dapr_url(topic)
        print(f"[DAPR-PUB] Publishing to URL: {url}", file=sys.stderr)
        print(f"[DAPR-PUB] Payload keys: {list(data.keys())}", file=sys.stderr)

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(url, json=data)
                print(f"[DAPR-PUB] Response status: {response.status_code}", file=sys.stderr)
                print(f"[DAPR-PUB] Response body: {response.text[:200]}", file=sys.stderr)

                # Dapr HTTP publish returns 204 No Content on success
                if response.status_code in (200, 204):
                    print(f"[DAPR-PUB] Event published successfully to topic '{topic}': {data.get('task_id', 'N/A')}", file=sys.stderr)
                    return True
                else:
                    print(f"[DAPR-PUB] Failed to publish event to topic '{topic}': status={response.status_code}, body={response.text}", file=sys.stderr)
                    return False

        except httpx.ConnectError as e:
            # Dapr sidecar not available - log but don't fail the request
            print(f"[DAPR-PUB] ConnectError: Dapr sidecar not available at {self.dapr_host}:{self.dapr_port}. {e}", file=sys.stderr)
            return False
        except httpx.TimeoutException as e:
            print(f"[DAPR-PUB] Timeout publishing event to topic '{topic}': {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"[DAPR-PUB] Unexpected error publishing event to topic '{topic}': {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
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
