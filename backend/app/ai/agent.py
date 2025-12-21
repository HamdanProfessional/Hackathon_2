"""
Google Gemini Agent Service for Task Management

This module implements the stateless AI agent that processes user messages
and executes tool calls (like creating tasks) through Google Gemini's OpenAI-compatible interface.

Architecture (Stateless Request Cycle):
1. Load conversation history from ConversationManager
2. Build messages array with system prompt + history + new user message
3. Call Google Gemini API with tool definitions via OpenAI-compatible endpoint
4. Execute tool loop (if model requests tool calls)
5. Return final assistant response
6. Save new messages to ConversationManager

Security: user_id is injected into all tool calls from JWT authentication.
"""

from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.ai.tools import add_task, list_tasks, complete_task, update_task, delete_task, AVAILABLE_TOOLS
from app.ai.mcp_tools import mcp, set_mcp_context, clear_mcp_context
from app.ai.conversation_manager import ConversationManager
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
        # For Gemini, we need to add the API key to the Authorization header
        # Create a custom HTTP client that intercepts requests
        class GeminiAuthenticatedClient(httpx.AsyncClient):
            def __init__(self, api_key: str, **kwargs):
                self.api_key = api_key
                super().__init__(**kwargs)

            async def send(self, request, **kwargs):
                # Add Authorization header for Gemini API
                # Gemini expects: Bearer <api_key>
                request.headers["Authorization"] = f"Bearer {self.api_key}"
                return await super().send(request, **kwargs)

        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,  # Use actual API key
            base_url=settings.AI_BASE_URL,
            http_client=GeminiAuthenticatedClient(api_key=settings.AI_API_KEY)
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
        return f"""You are a bilingual Todo Assistant. You can speak fluent Urdu and English. Detect the user's language from their message. If they speak Urdu, reply in Urdu. If they speak English, reply in English. Ensure task titles retain their original language unless explicitly asked to translate. You help users manage their todo tasks naturally in their preferred language.

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
        Run the agent with tool calling support and enhanced error handling.

        This is the main entry point for processing user messages with improved
        resilience, retry logic, and graceful degradation.

        Flow:
        1. Validate input and preprocess message
        2. Build messages array (system + history + user message)
        3. Call OpenAI with tool definitions (with retry logic)
        4. If tool calls requested, execute them with error handling
        5. Return final response with fallback options

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
                - error: Error information if applicable (Optional[dict])
        """
        import asyncio
        from datetime import datetime

        # Input validation
        if not user_message or not user_message.strip():
            return {
                "response": "Please provide a message. How can I help you manage your tasks today?",
                "tool_calls": [],
                "messages": [],
                "error": {"type": "empty_input", "message": "Empty user message"}
            }

        # Enhanced language detection for better Urdu/English handling
        detected_language = self._detect_language(user_message)

        # Build messages array with enhanced context
        messages = [
            {"role": "system", "content": self._build_system_prompt(user_id)}
        ]

        # Add conversation history (limit last 10 messages for context)
        messages.extend(history[-10:] if len(history) > 10 else history)

        # Add new user message with language context
        messages.append({
            "role": "user",
            "content": f"[Language: {detected_language}] {user_message}"
        })

        # Prepare tool schemas
        tools = [
            AVAILABLE_TOOLS["add_task"]["schema"],
            AVAILABLE_TOOLS["list_tasks"]["schema"],
            AVAILABLE_TOOLS["complete_task"]["schema"],
            AVAILABLE_TOOLS["update_task"]["schema"],
            AVAILABLE_TOOLS["delete_task"]["schema"]
        ]

        # Track tool calls made and execution metadata
        tool_calls_made = []
        execution_start = datetime.now()

        # Tool execution loop with enhanced retry logic
        max_iterations = 5
        retry_count = 0
        max_retries = 2

        for iteration in range(max_iterations):
            try:
                # Call OpenAI API with enhanced error handling and retry logic
                response = await self._call_api_with_retry(
                    messages=messages,
                    tools=tools,
                    max_retries=max_retries
                )

            except Exception as e:
                # Enhanced error handling with categorization
                error_info = self._categorize_error(e)

                # Log error with context
                import traceback
                print(f"[AGENT ERROR] {error_info['type']}: {error_info['message']}")
                print(f"[AGENT CONTEXT] User: {user_id}, Iteration: {iteration}")
                print(f"[AGENT TRACEBACK] {traceback.format_exc()}")

                # Determine fallback strategy
                if error_info['type'] == 'rate_limit':
                    # Implement exponential backoff suggestion
                    wait_time = min(2 ** retry_count, 10)
                    return {
                        "response": f"I'm experiencing high demand. Please wait {wait_time} seconds and try again." if detected_language == 'en'
                                 else f"مجھے زیادہ طلب ہو رہی ہے۔ براہ کرم {wait_time} سیکنڈ انتظار کریں اور دوبارہ کوشش کریں۔",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:],
                        "error": error_info,
                        "retry_suggested": wait_time
                    }
                elif error_info['type'] in ['connection', 'timeout']:
                    return {
                        "response": "I'm having connection issues. Please check your internet and try again." if detected_language == 'en'
                                 else "مجھے کنکشن کی مشکلات ہو رہی ہیں۔ براہ کرم اپنے انٹرنیٹ کو چیک کریں اور دوبارہ کوشش کریں۔",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:],
                        "error": error_info
                    }
                elif error_info['type'] == 'authentication':
                    return {
                        "response": "There's a configuration issue with the AI service. This has been logged and will be addressed." if detected_language == 'en'
                                 else "AI سروس کے ساتھ ترتیب کا مسئلہ ہے۔ اس کو لاگ کر دیا گیا ہے اور اس کا حل کیا جائے گا۔",
                        "tool_calls": tool_calls_made,
                        "messages": messages[len(history) + 1:],
                        "error": error_info
                    }
                else:
                    # For unknown errors, try graceful degradation
                    return await self._graceful_degradation(user_message, detected_language, tool_calls_made, error_info)

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

                # Set MCP context for tool execution
                set_mcp_context(db, user_id)

                try:
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

                finally:
                    # Clear MCP context
                    clear_mcp_context()

                # Continue loop to get final response
                continue
            else:
                # No tool calls, we have the final response
                final_response = assistant_message.content or ""

                # Clear MCP context
                clear_mcp_context()

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

    def _detect_language(self, text: str) -> str:
        """
        Enhanced language detection for Urdu and English.

        Uses character analysis and common Urdu/English word detection.
        """
        import re

        # Check for Urdu characters (Unicode range for Urdu)
        urdu_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        total_chars = len(re.sub(r'\s', '', text))  # Exclude spaces

        # If more than 30% characters are Urdu, classify as Urdu
        if total_chars > 0 and (urdu_chars / total_chars) > 0.3:
            return 'ur'

        # Common Urdu indicators
        urdu_indicators = ['ہے', 'ہیں', 'کے', 'کی', 'کا', 'گے', 'گی', 'ہوں', 'ہو', 'کرنا', 'دینا', 'لینا']
        for indicator in urdu_indicators:
            if indicator in text:
                return 'ur'

        # Default to English
        return 'en'

    async def _call_api_with_retry(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict],
        max_retries: int = 2
    ) -> Any:
        """
        Call the OpenAI API with retry logic and exponential backoff.
        """
        import asyncio

        for attempt in range(max_retries + 1):
            try:
                return await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
            except Exception as e:
                if attempt == max_retries:
                    raise  # Re-raise if we've exhausted retries

                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

    def _categorize_error(self, error: Exception) -> Dict[str, Any]:
        """
        Categorize errors for better handling and user messaging.
        """
        error_type = type(error).__name__
        error_message = str(error)

        if "RateLimitError" in error_type or "rate limit" in error_message.lower():
            return {
                "type": "rate_limit",
                "message": "API rate limit exceeded",
                "retryable": True
            }
        elif "APIConnectionError" in error_type or "connection" in error_message.lower():
            return {
                "type": "connection",
                "message": "API connection failed",
                "retryable": True
            }
        elif "TimeoutError" in error_type or "timeout" in error_message.lower():
            return {
                "type": "timeout",
                "message": "API request timeout",
                "retryable": True
            }
        elif "AuthenticationError" in error_type or "auth" in error_message.lower():
            return {
                "type": "authentication",
                "message": "API authentication failed",
                "retryable": False
            }
        else:
            return {
                "type": "unknown",
                "message": error_message,
                "retryable": False
            }

    async def _graceful_degradation(
        self,
        user_message: str,
        language: str,
        tool_calls_made: List[Dict],
        error_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide a fallback response when the AI service fails.

        This method uses pattern matching to provide basic task management
        functionality even when the main AI service is unavailable.
        """
        message_lower = user_message.lower()

        # Simple pattern matching for basic responses
        if any(word in message_lower for word in ['hello', 'hi', 'ہیلو', 'سلام']):
            response = "Hello! I'm here to help you manage your tasks. You can ask me to create, list, complete, update, or delete tasks." if language == 'en' \
                      else "سلام! میں آپ کے ٹاسکس منیج کرنے میں آپ کی مدد کرنے کے لیے ہاں۔ آپ مجھ سے ٹاسکس بنانے، فہرست دکھانے، مکمل کرنے، اپ ڈیٹ کرنے، یا حذف کرنے کے لیے پوچھ سکتے ہیں۔"

        elif any(word in message_lower for word in ['help', 'مدد']):
            response = "I can help you with task management. Try saying things like:\n- 'Create a task called Finish project'\n- 'Show my tasks'\n- 'Mark task as complete'\n- 'Delete a task'" if language == 'en' \
                      else "میں آپ کی ٹاسک مینجمنٹ میں مدد کر سکتا ہوں۔ ایسی باتیں کہنے کی کوشش کریں:\n- 'فنش پروجیکٹ نام کا ٹاسک بنائیں'\n- 'میرے ٹاسکس دکھائیں'\n- 'ٹاسک کو مکمل کے طور پر مارک کریں'\n- 'ٹاسک حذف کریں'"

        elif any(word in message_lower for word in ['task', 'ٹاسک', 'create', 'add', 'بنائیں', 'شامل کریں']):
            response = "I understand you want to manage a task. Due to technical difficulties, please use the web interface to create or modify tasks for now." if language == 'en' \
                      else "میں سمجھتا ہوں کہ آپ ٹاسک منیج کرنا چاہتے ہیں۔ تکنیکی مشکلات کی وجہ سے، براہ کرم ابھی کے لیے ٹاسکس بنانے یا تبدیل کرنے کے لیے ویب انٹرفیس استعمال کریں۔"

        else:
            response = "I'm experiencing technical difficulties right now. Please try again later or use the web interface to manage your tasks." if language == 'en' \
                      else "میں ابھی تکنیکی مشکلات کا سامنا کر رہا ہوں۔ براہ کرم بعد میں دوبارہ کوشش کریں یا اپنے ٹاسکس منیج کرنے کے لیے ویب انٹرفیس استعمال کریں۔"

        return {
            "response": response,
            "tool_calls": tool_calls_made,
            "messages": [{"role": "assistant", "content": response}],
            "error": error_info,
            "fallback_mode": True
        }

    async def process_message(
        self,
        db: AsyncSession,
        user_id: int,
        user_message: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a user message with full conversation management.

        This method:
        1. Loads conversation history (if conversation_id provided)
        2. Runs the agent with the message and history
        3. Saves the new messages to the conversation
        4. Returns the response with conversation_id

        Args:
            db: Database session
            user_id: Authenticated user ID
            user_message: User's message
            conversation_id: Optional existing conversation ID

        Returns:
            Dict with:
                - response: Assistant's response
                - conversation_id: The conversation ID (new or existing)
                - tool_calls: List of tool calls made
        """
        # Initialize conversation manager
        conversation_manager = ConversationManager(db)

        # Create new conversation if needed
        if not conversation_id:
            from app.models.user import User
            # Get user UUID from user_id (int)
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user:
                raise ValueError("User not found")
            conversation_id = await conversation_manager.create_conversation(user.id)

        # Load conversation history
        history = await conversation_manager.get_history(conversation_id)

        # Run agent with history
        result = await self.run_agent(db, user_id, user_message, history)

        # Save messages to conversation
        # Save user message
        await conversation_manager.save_message(
            conversation_id=conversation_id,
            role="user",
            content=user_message
        )

        # Save assistant response
        await conversation_manager.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["response"]
        )

        # Add conversation_id to result
        result["conversation_id"] = conversation_id

        return result
