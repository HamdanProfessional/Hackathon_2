"""
Mock AI Agent Service for Phase 3 Testing (without requiring real API key)

This mock service simulates AI responses for task management operations.
It follows the same interface as the real AgentService but returns predefined responses.
"""

from typing import Dict, List, Any, Optional
import json
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.ai.tools import add_task, list_tasks, complete_task, update_task, delete_task
from app.ai.conversation_manager import ConversationManager


class MockAgentService:
    """
    Mock AI agent service for testing Phase 3 functionality without API keys.

    This service simulates AI responses based on simple pattern matching
    of user messages to task operations.
    """

    def __init__(self):
        """Initialize the mock agent service."""
        pass

    def _build_system_prompt(self, user_id: UUID) -> str:
        """Build system prompt (not used in mock but keeping interface)."""
        return f"Mock AI agent for user {user_id}"

    def _parse_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Parse user intent from message using simple pattern matching.

        Returns dict with:
        - intent: 'create_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task', 'chat'
        - parameters: extracted parameters for the intent
        """
        message_lower = user_message.lower()

        # Create task patterns
        if any(word in message_lower for word in ['create', 'add', 'make a task', 'new task']):
            return {
                'intent': 'create_task',
                'parameters': {
                    'title': self._extract_task_title(user_message),
                    'priority': self._extract_priority(message_lower),
                    'description': user_message
                }
            }

        # List tasks patterns
        if any(word in message_lower for word in ['list', 'show', 'see', 'what', 'tasks']):
            return {
                'intent': 'list_tasks',
                'parameters': {
                    'status': self._extract_status_filter(message_lower),
                    'priority': self._extract_priority_filter(message_lower)
                }
            }

        # Complete task patterns
        if any(word in message_lower for word in ['complete', 'finished', 'done', 'mark as complete']):
            return {
                'intent': 'complete_task',
                'parameters': {
                    'description': self._extract_task_description(user_message)
                }
            }

        # Update task patterns
        if any(word in message_lower for word in ['update', 'change', 'modify', 'rename']):
            return {
                'intent': 'update_task',
                'parameters': {
                    'description': self._extract_task_description(user_message),
                    'updates': self._extract_updates(user_message)
                }
            }

        # Delete task patterns
        if any(word in message_lower for word in ['delete', 'remove']):
            return {
                'intent': 'delete_task',
                'parameters': {
                    'description': self._extract_task_description(user_message)
                }
            }

        # Default to chat
        return {
            'intent': 'chat',
            'parameters': {
                'response': self._generate_chat_response(user_message)
            }
        }

    def _extract_task_title(self, message: str) -> str:
        """Extract task title from message."""
        # Simple extraction - look for patterns like "create X" or "add X"
        import re

        # Pattern: create/add/make 'task' [called/named] TITLE
        patterns = [
            r'(?:create|add|make a? task(?: called| named)?)\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:create|add|make a?)\s+[\'"]*([^\'"\.]+)[\'"]*\s+task',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Fallback - use first 50 chars
        return message[:50] + "..." if len(message) > 50 else message

    def _extract_priority(self, message: str) -> str:
        """Extract priority from message."""
        if any(word in message for word in ['high', 'urgent', 'important']):
            return 'high'
        elif any(word in message for word in ['low', 'minor']):
            return 'low'
        else:
            return 'medium'  # Default

    def _extract_status_filter(self, message: str) -> str:
        """Extract status filter from message."""
        if any(word in message for word in ['completed', 'finished', 'done']):
            return 'completed'
        elif any(word in message for word in ['pending', 'active', 'not done']):
            return 'pending'
        else:
            return 'all'  # Default

    def _extract_priority_filter(self, message: str) -> str:
        """Extract priority filter from message."""
        if 'high' in message:
            return 'high'
        elif 'low' in message:
            return 'low'
        elif 'medium' in message:
            return 'medium'
        else:
            return ''  # No filter

    def _extract_task_description(self, message: str) -> str:
        """Extract task description for operations."""
        # Look for task references like "the X task" or "task X"
        import re

        patterns = [
            r'(?:the|task)\s+[\'"]*([^\'"\.]+)[\'"]*\s+task',
            r'(?:complete|update|delete)\s+(?:the\s+)?[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:mark|finish)\s+[\'"]*([^\'"\.]+)[\'"]*',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Return a portion of the message
        return message[:30]

    def _extract_updates(self, message: str) -> Dict[str, Any]:
        """Extract updates for task operations."""
        updates = {}
        message_lower = message.lower()

        # Priority updates
        if any(word in message_lower for word in ['priority to high', 'high priority']):
            updates['priority'] = 'high'
        elif any(word in message_lower for word in ['priority to low', 'low priority']):
            updates['priority'] = 'low'

        # Title updates (rename)
        import re
        rename_pattern = r'(?:rename|to)\s+[\'"]*([^\'"\.]+)[\'"]*'
        match = re.search(rename_pattern, message)
        if match:
            updates['title'] = match.group(1).strip()

        return updates

    def _generate_chat_response(self, message: str) -> str:
        """Generate a generic chat response."""
        if any(word in message.lower() for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm here to help you manage your tasks. You can ask me to create, list, complete, update, or delete tasks."
        elif 'help' in message.lower():
            return "I can help you with task management. Try saying things like:\n- 'Create a task called Finish project'\n- 'List all my tasks'\n- 'Mark the project task as complete'\n- 'Delete the shopping task'"
        else:
            return "I'm a mock AI assistant for task management. I can help you create, list, complete, update, or delete tasks."

    async def run_agent(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Run the mock agent with simulated tool execution.

        Args:
            db: Database session (for tool execution)
            user_id: Authenticated user ID
            user_message: User's message
            history: Conversation history (not used in mock)

        Returns:
            Dict with response and tool_calls made
        """
        # Parse user intent
        parsed = self._parse_intent(user_message)
        intent = parsed['intent']
        parameters = parsed['parameters']

        tool_calls_made = []
        response_text = ""

        # Execute based on intent
        if intent == 'create_task':
            result = await add_task(
                db=db,
                user_id=user_id,
                title=parameters['title'],
                priority=parameters['priority'],
                description=parameters['description']
            )
            tool_calls_made.append({'name': 'add_task', 'parameters': parameters})
            response_text = f"I've created a new task: '{parameters['title']}' with {parameters['priority']} priority."

        elif intent == 'list_tasks':
            result = await list_tasks(
                db=db,
                user_id=user_id,
                status=parameters.get('status', 'all'),
                priority=parameters.get('priority', '')
            )
            tool_calls_made.append({'name': 'list_tasks', 'parameters': parameters})

            if result and 'items' in result and result['items']:
                tasks = result['items']
                response_text = f"Found {len(tasks)} task(s):\n"
                for task in tasks[:5]:  # Show first 5 tasks
                    status_icon = "✓" if task.get('completed') else "○"
                    response_text += f"\n{status_icon} **{task['title']}** (Priority: {task.get('priority', 'medium')})"
            else:
                response_text = "No tasks found matching your criteria."

        elif intent == 'complete_task':
            # First list tasks to find the one to complete
            tasks_result = await list_tasks(db=db, user_id=user_id)
            if tasks_result and 'items' in tasks_result and tasks_result['items']:
                # Simple matching - complete the first incomplete task
                task_to_complete = None
                for task in tasks_result['items']:
                    if not task.get('completed'):
                        task_to_complete = task
                        break

                if task_to_complete:
                    result = await complete_task(
                        db=db,
                        user_id=user_id,
                        task_id=task_to_complete['id']
                    )
                    tool_calls_made.append({'name': 'complete_task', 'parameters': {'task_id': task_to_complete['id']}})
                    response_text = f"Great! I've marked '{task_to_complete['title']}' as complete."
                else:
                    response_text = "No incomplete tasks found to complete."
            else:
                response_text = "No tasks found."

        elif intent == 'update_task':
            # Find a task to update (simplified)
            tasks_result = await list_tasks(db=db, user_id=user_id)
            if tasks_result and 'items' in tasks_result and tasks_result['items']:
                task_to_update = tasks_result['items'][0]  # Update first task
                updates = parameters['updates']
                if updates:
                    result = await update_task(
                        db=db,
                        user_id=user_id,
                        task_id=task_to_update['id'],
                        **updates
                    )
                    tool_calls_made.append({'name': 'update_task', 'parameters': {'task_id': task_to_update['id'], **updates}})
                    update_desc = ', '.join(f"{k}: {v}" for k, v in updates.items())
                    response_text = f"I've updated '{task_to_update['title']}' with {update_desc}."
                else:
                    response_text = "I'm not sure what updates you want to make to the task."
            else:
                response_text = "No tasks found to update."

        elif intent == 'delete_task':
            # Find a task to delete (simplified)
            tasks_result = await list_tasks(db=db, user_id=user_id)
            if tasks_result and 'items' in tasks_result and tasks_result['items']:
                task_to_delete = tasks_result['items'][0]  # Delete first task
                result = await delete_task(
                    db=db,
                    user_id=user_id,
                    task_id=task_to_delete['id']
                )
                tool_calls_made.append({'name': 'delete_task', 'parameters': {'task_id': task_to_delete['id']}})
                response_text = f"I've deleted the task '{task_to_delete['title']}'."
            else:
                response_text = "No tasks found to delete."

        else:  # chat
            response_text = parameters['response']

        return {
            "response": response_text,
            "tool_calls": tool_calls_made,
            "messages": [
                {"role": "assistant", "content": response_text}
            ]
        }

    async def process_message(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_message: str,
        conversation_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Process a user message with mock conversation management.

        Args:
            db: Database session
            user_id: Authenticated user ID
            user_message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            Dict with response and conversation_id
        """
        # For mock AI, create actual conversation in database
        conversation_manager = ConversationManager(db)
        if not conversation_id:
            # Create new conversation and return its UUID
            conversation_id = await conversation_manager.create_conversation(user_id)

        # Run agent
        try:
            result = await self.run_agent(db, user_id, user_message, [])
            print(f"[MOCK] Agent run successful", file=sys.stderr)
        except Exception as e:
            print(f"[MOCK] ERROR in run_agent: {e}", file=sys.stderr)
            print(f"[MOCK] ERROR type: {type(e)}", file=sys.stderr)
            import traceback
            print(f"[MOCK] TRACEBACK: {traceback.format_exc()}", file=sys.stderr)
            # Return a simple response even if agent fails
            result = {
                "response": "I encountered an error, but I'm still here to help!",
                "tool_calls": []
            }

        # Add conversation_id to result
        result["conversation_id"] = conversation_id
        print(f"[MOCK] Returning result with conversation_id: {conversation_id}", file=sys.stderr)

        return result