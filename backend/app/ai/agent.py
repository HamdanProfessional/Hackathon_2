"""
Google Gemini Agent Service for Task Management

This module implements the stateless AI agent that processes user messages
and executes tool calls (like creating tasks) through Google Gemini's OpenAI-compatible interface.

Architecture (Stateless Request Cycle):
1. Load conversation history from DB
2. Build messages array with system prompt + history + new user message
3. Call Google Gemini API with tool definitions via OpenAI-compatible endpoint
4. Execute tool loop (if model requests tool calls)
5. Return final assistant response

Security: user_id is injected into all tool calls from JWT authentication.
"""

from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.tools import AVAILABLE_TOOLS, add_task, list_tasks, complete_task, update_task, delete_task
from app.config import settings


class AgentService:
    """
    Stateless AI agent service using Google Gemini with OpenAI-compatible interface.

    This service orchestrates:
    - Chat completion with tool calling
    - Tool execution with user_id injection
    - Response formatting

    The agent does NOT persist state - history is loaded/saved by the endpoint.
    """

    def __init__(self):
        """
        Initialize AgentService with Google Gemini client via OpenAI-compatible interface.
        """
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL
        )
        self.model = settings.AI_MODEL

    def _build_system_prompt(self, user_id: int) -> str:
        """
        Build system prompt for the agent.

        Args:
            user_id: Current user ID (included for context)

        Returns:
            System prompt string
        """
        return f"""You are a helpful AI assistant that helps users manage their todo tasks.

You can:
- Create new tasks when users ask you to add, create, or make tasks
- List and filter tasks when users ask to see their tasks, todo list, or what's due
- Mark tasks as complete when users say they finished or completed a task
- Update task details when users want to modify, rename, or reschedule tasks
- Delete tasks when users explicitly request removal
- Understand natural language requests about tasks
- Provide helpful confirmations and responses

When listing tasks:
- Use the list_tasks tool to retrieve tasks
- Apply filters based on user requests:
  - "pending tasks" or "active tasks" → status="pending"
  - "completed tasks" or "finished tasks" → status="completed"
  - "all tasks" → status="all" (default)
  - "high priority tasks" → priority="high"
  - "tasks due today" or "today's tasks" → date_filter="today"
  - "tasks due tomorrow" → date_filter="tomorrow"
  - "overdue tasks" or "past due" → date_filter="overdue"
  - "this week's tasks" → date_filter="this_week"
- Format task lists as readable Markdown:
  - Use bullet points with task details
  - Example: "**Task Title** (Priority) - Due: Date"
  - Include status indicators (✓ for completed, ○ for pending)
- If no tasks match the criteria, respond with a friendly message like "You have no tasks matching that criteria" or "Your list is empty for this filter"

When completing tasks (IMPORTANT - Fuzzy Matching Strategy):
- If user mentions a task by name (e.g., "I finished the milk task" or "Complete buy groceries"):
  1. FIRST call list_tasks to find tasks matching that description
  2. Look for the task in the results (use fuzzy matching in your reasoning - similar titles count)
  3. THEN call complete_task with the specific task_id you found
- If user provides a task ID directly (rare), use it immediately
- If multiple tasks match the name, ask which one they mean
- The complete_task tool requires task_id - you cannot complete by name alone
- After completion, relay the confirmation message from the tool

When updating tasks (IMPORTANT - Partial Updates Strategy):
- If user mentions a task by name (e.g., "Rename Buy Milk to Buy Groceries" or "Reschedule the meeting to tomorrow"):
  1. FIRST call list_tasks to find the task
  2. THEN call update_task with ONLY the fields that need to change
- Only provide fields that the user wants to change - omit fields that should stay the same
- Examples:
  - "Reschedule to tomorrow" → update_task(task_id=X, due_date="2025-12-18") - ONLY due_date
  - "Rename to 'New Name'" → update_task(task_id=X, title="New Name") - ONLY title
  - "Change priority to high" → update_task(task_id=X, priority="high") - ONLY priority
- Date calculations: If user says "tomorrow", "next week", etc., calculate the actual date in YYYY-MM-DD format
- After updating, relay the specific changes made from the confirmation message

When deleting tasks (CRITICAL - Safety Protocol):
- Deletion is PERMANENT and DESTRUCTIVE - be absolutely certain before executing
- If user mentions task by name (e.g., "Delete the milk task" or "Remove the meeting"):
  1. FIRST call list_tasks to find the task
  2. VERIFY you found the correct task
  3. If MULTIPLE tasks match, STOP and ask: "I found multiple tasks. Which one did you want to delete: [list them]?"
  4. If SINGLE task matches, proceed with delete_task(task_id=X)
- If user says "Delete task 5" (provides ID), you may execute immediately
- NEVER delete without being certain of the task identity
- After deletion, relay the confirmation message from the tool
- If user seems uncertain or says "cancel", "wait", "nevermind" - do NOT execute the deletion

Guidelines:
- Be concise and friendly
- When creating tasks, confirm what you created with details
- When completing tasks, provide encouraging confirmation (e.g., "Great job! I've marked 'Buy Milk' as complete.")
- When updating tasks, confirm exactly what changed (e.g., "I've updated the due date for 'Team Meeting' to tomorrow.")
- When deleting tasks, confirm the removal (e.g., "I have removed 'Buy Milk' from your list.")
- When listing tasks, format them clearly and readably
- If the request is unclear, ask for clarification (e.g., "Which task did you want to update?" or "Which task should I delete?")
- Extract task details (title, description, priority, due date) from natural language
- Combine filters naturally (e.g., "high priority tasks due today" uses both priority and date_filter)
- For destructive operations (deletion), prioritize safety and ask for confirmation if there's any ambiguity

Current User ID: {user_id} (for internal use only, don't mention this to the user)"""

    async def run_agent(
        self,
        db: AsyncSession,
        user_id: int,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Run the agent with tool calling support.

        This is the main entry point for processing user messages.

        Flow:
        1. Build messages array (system + history + user message)
        2. Call OpenAI with tool definitions
        3. If tool calls requested, execute them and call again
        4. Return final response

        Args:
            db: Database session (for tool execution)
            user_id: Authenticated user ID (injected into tools)
            user_message: User's message
            history: Conversation history in format [{"role": "...", "content": "..."}]

        Returns:
            Dict with:
                - response: Final assistant message (str)
                - tool_calls: List of tool calls made (List[dict])
                - messages: All new messages to save (List[dict])
        """
        # Build messages array
        messages = [
            {"role": "system", "content": self._build_system_prompt(user_id)}
        ]

        # Add conversation history
        messages.extend(history)

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        # Prepare tool schemas
        tools = [
            AVAILABLE_TOOLS["add_task"]["schema"],
            AVAILABLE_TOOLS["list_tasks"]["schema"],
            AVAILABLE_TOOLS["complete_task"]["schema"],
            AVAILABLE_TOOLS["update_task"]["schema"],
            AVAILABLE_TOOLS["delete_task"]["schema"]
        ]

        # Track tool calls made
        tool_calls_made = []

        # Tool execution loop (max 5 iterations to prevent infinite loops)
        max_iterations = 5
        for iteration in range(max_iterations):
            try:
                # Call OpenAI API with error handling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
            except Exception as e:
                # Handle OpenAI API errors gracefully
                error_type = type(e).__name__

                # Rate limit errors
                if "RateLimitError" in error_type:
                    return {
                        "response": "I'm currently experiencing high demand. Please try again in a moment.",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:]
                    }

                # API connection errors
                if "APIConnectionError" in error_type or "APIError" in error_type:
                    return {
                        "response": "I'm having trouble connecting right now. Please check your internet connection and try again.",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:]
                    }

                # Authentication errors
                if "AuthenticationError" in error_type:
                    return {
                        "response": "There's a configuration issue with the AI service. Please contact support.",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:]
                    }

                # Generic error fallback
                return {
                    "response": "I encountered an unexpected error. Please try again, and if the problem persists, contact support.",
                    "tool_calls": tool_calls_made,
                    "messages": messages[len(history) + 1:]
                }

            assistant_message = response.choices[0].message

            # Check if tool calls were requested
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to messages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Track tool call
                    tool_calls_made.append({
                        "name": function_name,
                        "arguments": function_args
                    })

                    # Execute tool (inject user_id and db)
                    if function_name == "add_task":
                        result = await add_task(
                            db=db,
                            user_id=user_id,  # Injected from JWT
                            **function_args
                        )
                    elif function_name == "list_tasks":
                        result = await list_tasks(
                            db=db,
                            user_id=user_id,  # Injected from JWT
                            **function_args
                        )
                    elif function_name == "complete_task":
                        result = await complete_task(
                            db=db,
                            user_id=user_id,  # Injected from JWT
                            **function_args
                        )
                    elif function_name == "update_task":
                        result = await update_task(
                            db=db,
                            user_id=user_id,  # Injected from JWT
                            **function_args
                        )
                    elif function_name == "delete_task":
                        result = await delete_task(
                            db=db,
                            user_id=user_id,  # Injected from JWT
                            **function_args
                        )
                    else:
                        result = {"status": "error", "message": f"Unknown tool: {function_name}"}

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": json.dumps(result)
                    })

                # Continue loop to get final response
                continue
            else:
                # No tool calls, we have the final response
                final_response = assistant_message.content or ""

                # Return result
                return {
                    "response": final_response,
                    "tool_calls": tool_calls_made,
                    "messages": messages[len(history) + 1:]  # Only new messages (after history)
                }

        # Max iterations reached (shouldn't happen normally)
        return {
            "response": "I apologize, but I encountered an issue processing your request. Please try again.",
            "tool_calls": tool_calls_made,
            "messages": messages[len(history) + 1:]
        }
