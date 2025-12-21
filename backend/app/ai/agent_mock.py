"""
Improved Mock AI Agent Service for Phase 3 Testing (without requiring real API key)

This enhanced mock service simulates AI responses for task management operations with:
- Sophisticated pattern matching for better intent recognition
- Support for task completion, updates, and deletions with task name matching
- Multi-step operations (finding tasks before updating/deleting)
- Natural language understanding for dates, priorities, and task references
- Fallback mechanisms for ambiguous requests

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
        Parse user intent from message using improved pattern matching.

        Returns dict with:
        - intent: 'create_task', 'list_tasks', 'complete_task', 'update_task', 'delete_task', 'chat'
        - parameters: extracted parameters for the intent
        - task_reference: task name or identifier when provided
        """
        message_lower = user_message.lower()
        original_message = user_message  # Keep original case for extraction

        # Create task patterns - enhanced with more variations
        create_patterns = [
            'create', 'add', 'make a task', 'new task', 'add a new',
            'i need to', 'i have to', 'remind me to', 'don\'t forget to'
        ]
        if any(word in message_lower for word in create_patterns):
            # Check if this is actually a create operation and not just mentioning these words
            # Avoid false positives like "show me how to create..."
            if not any(word in message_lower for word in ['how to', 'show me', 'what is']):
                return {
                    'intent': 'create_task',
                    'parameters': {
                        'title': self._extract_task_title(original_message),
                        'priority': self._extract_priority(message_lower),
                        'description': self._extract_description(original_message),
                        'due_date': self._extract_due_date(message_lower)
                    }
                }

        # List tasks patterns - enhanced
        list_patterns = [
            'list', 'show', 'see', 'tasks', 'todo list', 'todo\'s',
            'my tasks', 'all my tasks', 'get my tasks', 'display'
        ]
        if any(pattern in message_lower for pattern in list_patterns):
            # Allow "what" for "what are my tasks" but exclude "what is/are/how to" questions
            if not any(word in message_lower for word in ['what is a', 'what is the', 'how to']):
                return {
                    'intent': 'list_tasks',
                    'parameters': {
                        'status': self._extract_status_filter(message_lower),
                        'priority': self._extract_priority_filter(message_lower),
                        'date_filter': self._extract_date_filter(message_lower)
                    }
                }

        # Complete task patterns - significantly enhanced
        complete_patterns = [
            'complete', 'completed', 'finish', 'finished', 'done', 'mark as complete',
            'mark complete', 'task is done', 'i finished', 'i completed',
            'i did', 'i accomplished', 'check off', 'tick off'
        ]
        if any(pattern in message_lower for pattern in complete_patterns):
            # Avoid false positives with change/update patterns
            if not any(word in message_lower for word in ['change', 'update', 'rename', 'modify']):
                return {
                    'intent': 'complete_task',
                    'parameters': {
                        'task_reference': self._extract_task_reference(original_message),
                        'task_id': None  # Will be determined after listing tasks
                    }
                }

        # Update task patterns - significantly enhanced
        update_patterns = [
            'update', 'change', 'modify', 'rename', 'edit', 'adjust',
            'reschedule', 'move to', 'move the', 'set priority', 'change priority',
            'change title', 'rename to', 'update title'
        ]
        if any(pattern in message_lower for pattern in update_patterns):
            return {
                'intent': 'update_task',
                'parameters': {
                    'task_reference': self._extract_task_reference(original_message),
                    'updates': self._extract_updates(original_message),
                    'task_id': None  # Will be determined after listing tasks
                }
            }

        # Delete task patterns - enhanced
        delete_patterns = [
            'delete', 'remove', 'eliminate', 'get rid of', 'trash',
            'cancel', 'scrap', 'discard', 'delete the task'
        ]
        if any(pattern in message_lower for pattern in delete_patterns):
            # Avoid false positives like "how do I delete"
            if not any(word in message_lower for word in ['how do', 'how to', 'can i']):
                return {
                    'intent': 'delete_task',
                    'parameters': {
                        'task_reference': self._extract_task_reference(original_message),
                        'task_id': None  # Will be determined after listing tasks
                    }
                }

        # Default to chat
        return {
            'intent': 'chat',
            'parameters': {
                'response': self._generate_chat_response(original_message)
            }
        }

    def _extract_task_title(self, message: str) -> str:
        """Extract task title from message."""
        import re

        # Pattern: create/add/make/remind me 'to' TITLE
        patterns = [
            r'(?:create|add|make|add a) (?:task )?(?:called|named)?\s*[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:remind me|don\'t forget|i need to|i have to)\s+to\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:create|add|make a?)\s+[\'"]*([^\'"\.]+)[\'"]*\s+task',
            r'new task[^\w]*[\'"]*([^\'"\.]+)[\'"]*',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Remove trailing task indicators
                title = re.sub(r'\s+(?:task|todo|item)\s*$', '', title, flags=re.IGNORECASE)
                if title and len(title) > 0:
                    return title

        # Try to extract the main action phrase
        # Look for "to [verb] [object]" patterns
        to_pattern = r'(?:to|for)\s+([a-z]+\s+(?:the\s+)?[a-zA-Z\s]+)'
        match = re.search(to_pattern, message, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Remove common stop words and limit length
            title = re.sub(r'\b(the|a|an|my|our)\b\s*', '', title, flags=re.IGNORECASE).strip()
            if title and 3 < len(title) < 100:
                return title.capitalize()

        # Fallback - use meaningful part of message
        cleaned = re.sub(r'^(?:please|can you|could you|i need to|i want to|remind me to|don\'t forget to)\s+', '', message, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+task\s*$', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        if cleaned:
            # Take first reasonable chunk
            return cleaned[:50] + "..." if len(cleaned) > 50 else cleaned

        return "New Task"

    def _extract_description(self, message: str) -> str:
        """Extract task description from message."""
        # Return the full message as description for now
        # In a more sophisticated version, we could extract additional details
        return message[:200] + "..." if len(message) > 200 else message

    def _extract_due_date(self, message: str) -> Optional[str]:
        """Extract due date from message."""
        import re
        from datetime import date, timedelta

        today = date.today()

        # Today, tomorrow, yesterday patterns
        if any(word in message for word in ['today', 'now']):
            return today.isoformat()
        elif 'tomorrow' in message:
            return (today + timedelta(days=1)).isoformat()
        elif 'yesterday' in message:
            return (today - timedelta(days=1)).isoformat()

        # Day of week patterns
        days_of_week = {
            'monday': 0, 'tues': 1, 'tue': 1, 'tuesday': 1,
            'wednes': 2, 'wed': 2, 'wednesday': 2,
            'thurs': 3, 'thu': 3, 'thursday': 3,
            'fri': 4, 'friday': 4,
            'satur': 5, 'sat': 5, 'saturday': 5,
            'sun': 6, 'sunday': 6
        }

        for day_name, day_num in days_of_week.items():
            if day_name in message:
                current_day = today.weekday()
                days_ahead = (day_num - current_day) % 7
                if days_ahead == 0:
                    days_ahead = 7  # Next week if it's today
                target_date = today + timedelta(days=days_ahead)
                return target_date.isoformat()

        # Numeric date patterns (MM/DD, DD/MM, etc.)
        date_patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD first (highest priority)
            r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?',  # MM/DD/YYYY or DD/MM/YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                try:
                    # Handle YYYY-MM-DD format first
                    if pattern == date_patterns[0] and len(groups) == 3:
                        year = int(groups[0])
                        month = int(groups[1])
                        day = int(groups[2])
                    elif len(groups) == 3 and groups[2]:  # Has year for MM/DD format
                        if len(groups[2]) == 2:  # YY format
                            year = 2000 + int(groups[2])
                        else:
                            year = int(groups[2])

                        # Try MM/DD/YYYY first
                        if int(groups[0]) <= 12:
                            month = int(groups[0])
                            day = int(groups[1])
                        else:  # Assume DD/MM/YYYY
                            day = int(groups[0])
                            month = int(groups[1])
                    elif len(groups) == 2:  # MM/DD or DD/MM format
                        month = int(groups[0])
                        day = int(groups[1])
                        year = today.year

                        # If the month > 12, swap
                        if month > 12:
                            month, day = day, month
                    else:
                        continue

                    # Validate date
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        return date(year, month, day).isoformat()
                except (ValueError, TypeError):
                    continue

        # Relative date patterns
        if any(word in message for word in ['next week', 'in a week']):
            return (today + timedelta(days=7)).isoformat()
        elif any(word in message for word in ['in 2 days', 'two days']):
            return (today + timedelta(days=2)).isoformat()
        elif any(word in message for word in ['in 3 days', 'three days']):
            return (today + timedelta(days=3)).isoformat()

        return None

    def _extract_date_filter(self, message: str) -> Optional[str]:
        """Extract date filter for listing tasks."""
        if any(word in message for word in ['today', 'due today']):
            return 'today'
        elif any(word in message for word in ['tomorrow', 'due tomorrow']):
            return 'tomorrow'
        elif any(word in message for word in ['overdue', 'past due']):
            return 'overdue'
        elif any(word in message for word in ['this week', 'week']):
            return 'this_week'
        return None

    def _extract_task_reference(self, message: str) -> Optional[str]:
        """Extract task reference (name or description) from message."""
        import re

        # First try to extract quoted text (highest priority)
        quote_pattern = r'[\'"]([^\'"]+)[\'"]'
        match = re.search(quote_pattern, message)
        if match:
            return match.group(1).strip()

        # Patterns for task references
        patterns = [
            r'(?:complete|update|delete|remove|finish|mark|check|tick)\s+(?:the\s+)?task\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:complete|update|delete|remove|finish|mark|check|tick)\s+(?:the\s+)?[\'"]*([^\'"\.]+)[\'"]*\s+task',
            r'(?:complete|update|delete|remove|finish)\s+(?:the\s+)?[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:rename|change)\s+(?:the\s+)?task\s+(?:to|as)?\s*[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:mark|check|tick)\s+off\s+(?:the\s+)?[\'"]*([^\'"\.]+)[\'"]*',
            r'task\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:the\s+)?task\s+[\'"]*([^\'"\.]+)[\'"]*',
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                reference = match.group(1).strip()
                # Clean up common trailing words
                reference = re.sub(r'\s+(?:task|todo|item)\s*$', '', reference, flags=re.IGNORECASE)
                # Remove trailing prepositions
                reference = re.sub(r'\s+(?:to|as|for|with|by)\s*$', '', reference, flags=re.IGNORECASE)
                if reference and len(reference) > 0:
                    return reference

        # Look for "the [something]" pattern
        the_pattern = r'(?:complete|update|delete|remove|finish|mark)\s+the\s+([a-zA-Z\s]{2,30})\s+(?:task|todo|item)?'
        match = re.search(the_pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

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
        import re
        updates = {}
        message_lower = message.lower()

        # Priority updates - enhanced patterns
        priority_patterns = {
            'high': [
                'priority to high', 'high priority', 'set priority high',
                'make it high', 'urgent', 'important', 'asap', 'high priority'
            ],
            'medium': [
                'priority to medium', 'medium priority', 'set priority medium',
                'make it medium', 'normal priority'
            ],
            'low': [
                'priority to low', 'low priority', 'set priority low',
                'make it low', 'minor', 'low priority'
            ]
        }

        for priority, patterns in priority_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                updates['priority'] = priority
                break

        # Title updates (rename) - enhanced
        rename_patterns = [
            r'rename\s+(?:it\s+)?(?:to|as)\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'change\s+(?:title|name)\s+(?:to|as)\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'(?:title|name)\s+(?:to|as)\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'update\s+(?:title|name)\s+(?:to|as)\s+[\'"]*([^\'"\.]+)[\'"]*',
            r'set\s+(?:title|name)\s+(?:to|as)\s+[\'"]*([^\'"\.]+)[\'"]*'
        ]

        for pattern in rename_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                new_title = match.group(1).strip()
                if len(new_title) > 0:
                    updates['title'] = new_title
                    break

        # Description updates
        desc_patterns = [
            r'(?:description|desc)\s+(?:to|as)\s+[\'"]*([^\'"]+)[\'"]*',
            r'add\s+(?:description|desc)\s+[\'"]*([^\'"]+)[\'"]*',
            r'set\s+(?:description|desc)\s+(?:to|as)\s+[\'"]*([^\'"]+)[\'"]*'
        ]

        for pattern in desc_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                new_desc = match.group(1).strip()
                if len(new_desc) > 0:
                    updates['description'] = new_desc
                    break

        # Due date updates
        due_date = self._extract_due_date(message_lower)
        if due_date and any(word in message_lower for word in ['reschedule', 'move to', 'move the', 'change date', 'due date', 'set due', 'deadline']):
            updates['due_date'] = due_date

        # Status updates (though mainly handled by complete_task)
        if any(word in message_lower for word in ['mark as pending', 'reopen', 'uncomplete']):
            updates['completed'] = False

        return updates

    def _generate_chat_response(self, message: str) -> str:
        """Generate a generic chat response."""
        message_lower = message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! I'm here to help you manage your tasks. I can create, list, complete, update, or delete tasks. Just tell me what you need!"
        elif 'help' in message_lower or 'what can you do' in message_lower:
            return """I can help you with task management in many ways:

**Creating tasks:**
- "Create a task called Finish project"
- "Add a task to buy groceries"
- "Remind me to call mom tomorrow"
- "I need to finish the report by Friday"

**Listing tasks:**
- "Show my tasks"
- "List all pending tasks"
- "What are my high priority tasks?"
- "Show tasks due today"

**Completing tasks:**
- "Mark 'Finish project' as complete"
- "I completed the shopping task"
- "Done with the homework"
- "Check off the meeting task"

**Updating tasks:**
- "Change priority of 'Finish project' to high"
- "Rename shopping task to grocery shopping"
- "Move the meeting to tomorrow"
- "Update the task description"

**Deleting tasks:**
- "Delete the old task"
- "Remove 'Finish project'"
- "Get rid of the shopping task"

I can understand natural language, so feel free to ask in your own words!"""
        else:
            return "I'm your AI task assistant. I can help you create, list, complete, update, or delete tasks. Try saying 'help' for examples or just tell me what you need!"

    async def run_agent(
        self,
        db: AsyncSession,
        user_id: UUID,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Run the mock agent with improved simulated tool execution.

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
                priority=parameters.get('priority', 'medium'),
                description=parameters.get('description', ''),
                due_date=parameters.get('due_date')
            )
            tool_calls_made.append({'name': 'add_task', 'parameters': parameters})

            if result.get('status') == 'success':
                priority_text = f" with {parameters.get('priority', 'medium')} priority"
                due_text = f" due {parameters['due_date']}" if parameters.get('due_date') else ""
                response_text = f"I've created a new task: '{parameters['title']}'{priority_text}{due_text}."
            else:
                response_text = f"I had trouble creating that task: {result.get('message', 'Unknown error')}"

        elif intent == 'list_tasks':
            result = await list_tasks(
                db=db,
                user_id=user_id,
                status=parameters.get('status', 'all'),
                priority=parameters.get('priority', ''),
                date_filter=parameters.get('date_filter')
            )
            tool_calls_made.append({'name': 'list_tasks', 'parameters': parameters})

            if result and result.get('status') == 'success' and result.get('tasks'):
                tasks = result['tasks']
                response_text = f"Found {len(tasks)} task(s):\n"
                for task in tasks[:10]:  # Show first 10 tasks
                    status_icon = "✓" if task.get('completed') else "○"
                    priority = task.get('priority', 'medium')
                    due_date = f" (Due: {task['due_date'][:10]})" if task.get('due_date') else ""
                    response_text += f"\n{status_icon} **{task['title']}** (Priority: {priority}{due_date})"
            else:
                response_text = "No tasks found matching your criteria."

        elif intent == 'complete_task':
            # Get all tasks first
            tasks_result = await list_tasks(db=db, user_id=user_id, status='pending')
            tool_calls_made.append({'name': 'list_tasks', 'parameters': {'status': 'pending'}})

            if tasks_result and tasks_result.get('status') == 'success' and tasks_result.get('tasks'):
                tasks = tasks_result['tasks']
                task_reference = parameters.get('task_reference')

                task_to_complete = None

                # If user specified a task, try to find it
                if task_reference:
                    for task in tasks:
                        # Check for exact title match
                        if task_reference.lower() == task['title'].lower():
                            task_to_complete = task
                            break
                        # Check for partial match
                        elif task_reference.lower() in task['title'].lower() or task['title'].lower() in task_reference.lower():
                            task_to_complete = task
                            break

                # If no specific task found, ask for clarification
                if not task_to_complete:
                    if task_reference:
                        response_text = f"I couldn't find a task matching '{task_reference}'. Here are your pending tasks:\n"
                        for i, task in enumerate(tasks[:5], 1):
                            response_text += f"\n{i}. {task['title']}"
                        response_text += "\n\nPlease specify which task you'd like to complete."
                    else:
                        # If no reference provided, complete the first task
                        task_to_complete = tasks[0]

                if task_to_complete:
                    result = await complete_task(
                        db=db,
                        user_id=user_id,
                        task_id=task_to_complete['id']
                    )
                    tool_calls_made.append({'name': 'complete_task', 'parameters': {'task_id': task_to_complete['id']}})

                    if result.get('status') == 'success':
                        response_text = f"Great! I've marked '{task_to_complete['title']}' as complete. 🎉"
                    else:
                        response_text = f"I had trouble marking that task complete: {result.get('message', 'Unknown error')}"
            else:
                response_text = "No pending tasks found to complete."

        elif intent == 'update_task':
            # Get all tasks first
            tasks_result = await list_tasks(db=db, user_id=user_id)
            tool_calls_made.append({'name': 'list_tasks', 'parameters': {}})

            if tasks_result and tasks_result.get('status') == 'success' and tasks_result.get('tasks'):
                tasks = tasks_result['tasks']
                task_reference = parameters.get('task_reference')
                updates = parameters.get('updates', {})

                task_to_update = None

                # If user specified a task, try to find it
                if task_reference:
                    for task in tasks:
                        if task_reference.lower() == task['title'].lower():
                            task_to_update = task
                            break
                        elif task_reference.lower() in task['title'].lower() or task['title'].lower() in task_reference.lower():
                            task_to_update = task
                            break

                # If no specific task found and user provided updates
                if not task_to_update:
                    if task_reference and updates:
                        response_text = f"I couldn't find a task matching '{task_reference}'. Here are your tasks:\n"
                        for i, task in enumerate(tasks[:5], 1):
                            status_icon = "✓" if task.get('completed') else "○"
                            response_text += f"\n{status_icon} {i}. {task['title']}"
                        response_text += "\n\nPlease specify which task you'd like to update."
                    elif updates:
                        # If no reference but updates provided, update the first task
                        task_to_update = tasks[0]
                    else:
                        response_text = "I'm not sure what updates you want to make. Please specify what you'd like to change."

                if task_to_update and updates:
                    result = await update_task(
                        db=db,
                        user_id=user_id,
                        task_id=task_to_update['id'],
                        **updates
                    )
                    tool_calls_made.append({'name': 'update_task', 'parameters': {'task_id': task_to_update['id'], **updates}})

                    if result.get('status') == 'success':
                        response_text = result.get('message', f"I've updated '{task_to_update['title']}'.")
                    else:
                        response_text = f"I had trouble updating that task: {result.get('message', 'Unknown error')}"
                elif task_to_update and not updates:
                    response_text = f"What would you like to update about '{task_to_update['title']}'? You can change the title, description, priority, or due date."
            else:
                response_text = "No tasks found to update."

        elif intent == 'delete_task':
            # Get all tasks first
            tasks_result = await list_tasks(db=db, user_id=user_id)
            tool_calls_made.append({'name': 'list_tasks', 'parameters': {}})

            if tasks_result and tasks_result.get('status') == 'success' and tasks_result.get('tasks'):
                tasks = tasks_result['tasks']
                task_reference = parameters.get('task_reference')

                task_to_delete = None

                # If user specified a task, try to find it
                if task_reference:
                    for task in tasks:
                        if task_reference.lower() == task['title'].lower():
                            task_to_delete = task
                            break
                        elif task_reference.lower() in task['title'].lower() or task['title'].lower() in task_reference.lower():
                            task_to_delete = task
                            break

                # If no specific task found, ask for clarification
                if not task_to_delete:
                    if task_reference:
                        response_text = f"I couldn't find a task matching '{task_reference}'. Here are your tasks:\n"
                        for i, task in enumerate(tasks[:5], 1):
                            status_icon = "✓" if task.get('completed') else "○"
                            response_text += f"\n{status_icon} {i}. {task['title']}"
                        response_text += "\n\nPlease specify which task you'd like to delete."
                    else:
                        response_text = "Which task would you like to delete? Please specify the task name."
                else:
                    # Confirmation before deletion
                    result = await delete_task(
                        db=db,
                        user_id=user_id,
                        task_id=task_to_delete['id']
                    )
                    tool_calls_made.append({'name': 'delete_task', 'parameters': {'task_id': task_to_delete['id']}})

                    if result.get('status') == 'success':
                        response_text = f"I've deleted the task '{task_to_delete['title']}'."
                    else:
                        response_text = f"I had trouble deleting that task: {result.get('message', 'Unknown error')}"
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
        import sys
        # For mock AI, create actual conversation in database
        conversation_manager = ConversationManager(db)
        if not conversation_id:
            # Create new conversation and return its UUID
            conversation_id = await conversation_manager.create_conversation(user_id)
            print(f"[MOCK] Created new conversation: {conversation_id}", file=sys.stderr)

        # Save the user message to the conversation
        try:
            await conversation_manager.save_message(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )
            print(f"[MOCK] Saved user message to conversation", file=sys.stderr)
        except Exception as e:
            print(f"[MOCK] ERROR saving user message: {e}", file=sys.stderr)
            import traceback
            print(f"[MOCK] TRACEBACK: {traceback.format_exc()}", file=sys.stderr)

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

        # Save the assistant response to the conversation
        try:
            if "response" in result:
                await conversation_manager.save_message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=result["response"]
                )
                print(f"[MOCK] Saved assistant response to conversation", file=sys.stderr)
        except Exception as e:
            print(f"[MOCK] ERROR saving assistant message: {e}", file=sys.stderr)
            import traceback
            print(f"[MOCK] TRACEBACK: {traceback.format_exc()}", file=sys.stderr)

        # Add conversation_id to result
        result["conversation_id"] = conversation_id
        print(f"[MOCK] Returning result with conversation_id: {conversation_id}", file=sys.stderr)

        return result