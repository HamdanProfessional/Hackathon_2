"""AI Agent Service for task management chatbot."""
from typing import List, Dict, Any, Optional
import os
from openai import AsyncOpenAI

from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task


class AgentService:
    """
    Service for managing AI agent interactions with MCP tools.

    This service configures the OpenAI agent with task management tools
    and handles conversation processing with security and token management.
    """

    def __init__(self, user_id: int, openai_api_key: Optional[str] = None):
        """
        Initialize agent service for a specific user.

        Args:
            user_id: ID of the authenticated user (injected into all tool calls)
            openai_api_key: OpenAI API key (defaults to env variable)
        """
        self.user_id = user_id
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.client = AsyncOpenAI(api_key=self.api_key)

        # System prompt defining agent behavior
        self.system_prompt = """You are a helpful task management assistant. You help users manage their to-do list through natural conversation.

**Your Capabilities:**
- Create tasks when users express intent to add, create, or remember something
- List tasks when users ask to see, show, view, or check their tasks
- Filter tasks by status (all, pending, or completed)
- Mark tasks as complete or incomplete when users indicate they finished something
- Update task titles or descriptions when users want to modify details
- Delete tasks when explicitly requested (ALWAYS ask confirmation first)
- Understand natural language inputs and extract task titles and descriptions
- Ask clarifying questions when user input is ambiguous

**Security Rules:**
- NEVER accept user_id from user input - it is automatically injected
- ALWAYS use the appropriate tool for each operation
- Extract clear, concise task titles from user messages
- If user provides description details, include them in the description parameter

**Response Style:**
- Be conversational and friendly
- Confirm actions with brief acknowledgments
- Format task lists clearly when displaying them
- Ask for clarification if the intent is unclear
- Stay focused on task management - politely redirect off-topic requests

**Tool Usage Patterns:**

*Creating Tasks:*
- User: "Add buy groceries to my list" → add_task(title="Buy groceries")
- User: "Remind me to call mom tomorrow" → add_task(title="Call mom")
- User: "I need to finish the report. It's Q4 analysis" → add_task(title="Finish the report", description="Q4 analysis")

*Listing Tasks:*
- User: "What's on my todo list?" → list_tasks(status="all")
- User: "Show me my tasks" → list_tasks(status="all")
- User: "What do I need to do?" → list_tasks(status="pending")
- User: "Show me completed tasks" → list_tasks(status="completed")
- User: "What's pending?" → list_tasks(status="pending")

*Completing Tasks:*
- User: "I finished buying groceries" → Find task matching "groceries", call complete_task(task_id=X)
- User: "Mark task 5 as done" → complete_task(task_id=5)
- User: "I'm done with the report" → Find task matching "report", mark complete

*Updating Tasks:*
- User: "Change task 3 to buy organic groceries" → update_task(task_id=3, title="Buy organic groceries")
- User: "Add description to task 2: needs review" → update_task(task_id=2, description="needs review")
- User: "Rename buy milk to buy dairy products" → Find task, update title

*Deleting Tasks (CRITICAL - ALWAYS CONFIRM FIRST):*
- User: "Delete task 5" → Ask: "Are you sure you want to delete task 5? This cannot be undone." Wait for "yes"
- User: "Remove old notes" → Find task, ask: "Are you sure you want to delete 'Old notes'?" Then delete if confirmed
- User confirms deletion → ONLY THEN call delete_task(task_id=X)

*Ambiguous Requests:*
- User: "Add something" → Ask: "What would you like to add to your list?"
- User: "Show me stuff" → Ask: "Would you like to see all your tasks, just pending ones, or completed ones?"
- User: "I finished it" → Ask: "Which task did you finish?" (if multiple tasks exist)
"""

    def create_agent_with_tools(self) -> List[Dict[str, Any]]:
        """
        Configure OpenAI function calling with MCP tools.

        Returns:
            List of tool definitions for OpenAI function calling
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the authenticated user. Use this when user expresses intent to create, add, or remember something.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title extracted from user's natural language input",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional detailed description of the task",
                            },
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve tasks for the authenticated user with optional filtering. Use this when user asks to see, show, list, or view their tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by completion status (default: all)",
                            },
                        },
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Toggle a task's completion status. Use when user indicates they finished a task or wants to mark it done/undone.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to toggle completion status",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update a task's title or description. Use when user wants to modify, change, or edit task details.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to update",
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional, provide only if changing)",
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional, provide only if changing)",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently delete a task. ALWAYS confirm with user before calling. Use when user wants to remove or delete a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "ID of the task to permanently delete",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            }
        ]
        return tools

    async def process_message(
        self, message_history: List[Dict[str, str]], user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message through the AI agent.

        Args:
            message_history: Previous conversation messages (list of {role, content})
            user_message: New user message to process

        Returns:
            Dict with:
                - response: AI assistant's text response
                - tool_calls: List of tools invoked (for tracking)

        Example:
            >>> result = await agent.process_message([], "Add buy milk")
            >>> result["response"]
            "I've added 'Buy milk' to your task list."
            >>> result["tool_calls"]
            [{"tool": "add_task", "parameters": {"title": "Buy milk"}}]
        """
        # Build messages array with system prompt
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        messages.extend(message_history)

        # Add new user message
        messages.append({"role": "user", "content": user_message})

        # Get tools configuration
        tools = self.create_agent_with_tools()

        # Call OpenAI API with function calling
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",  # Let model decide when to use tools
            )

            assistant_message = response.choices[0].message
            tool_calls_metadata = []

            # Handle tool calls if any
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = eval(tool_call.function.arguments)  # Parse JSON string

                    # Execute the appropriate tool
                    if function_name == "add_task":
                        # Inject user_id (SECURITY: never from user input)
                        result = await add_task(
                            user_id=self.user_id,
                            title=function_args.get("title"),
                            description=function_args.get("description", ""),
                        )

                        # Track tool call for response
                        tool_calls_metadata.append(
                            {
                                "tool": function_name,
                                "parameters": function_args,
                                "result": result,
                            }
                        )

                    elif function_name == "list_tasks":
                        # Inject user_id (SECURITY: never from user input)
                        result = await list_tasks(
                            user_id=self.user_id,
                            status=function_args.get("status", "all"),
                        )

                        # Track tool call for response
                        tool_calls_metadata.append(
                            {
                                "tool": function_name,
                                "parameters": function_args,
                                "result": result,
                            }
                        )

                    elif function_name == "complete_task":
                        # Inject user_id (SECURITY: never from user input)
                        result = await complete_task(
                            user_id=self.user_id,
                            task_id=function_args.get("task_id"),
                        )

                        # Track tool call for response
                        tool_calls_metadata.append(
                            {
                                "tool": function_name,
                                "parameters": function_args,
                                "result": result,
                            }
                        )

                    elif function_name == "update_task":
                        # Inject user_id (SECURITY: never from user input)
                        result = await update_task(
                            user_id=self.user_id,
                            task_id=function_args.get("task_id"),
                            title=function_args.get("title"),
                            description=function_args.get("description"),
                        )

                        # Track tool call for response
                        tool_calls_metadata.append(
                            {
                                "tool": function_name,
                                "parameters": function_args,
                                "result": result,
                            }
                        )

                    elif function_name == "delete_task":
                        # Inject user_id (SECURITY: never from user input)
                        result = await delete_task(
                            user_id=self.user_id,
                            task_id=function_args.get("task_id"),
                        )

                        # Track tool call for response
                        tool_calls_metadata.append(
                            {
                                "tool": function_name,
                                "parameters": function_args,
                                "result": result,
                            }
                        )

                # Generate follow-up response after tool execution
                # In a real implementation, we'd send the tool results back to the model
                # For now, we'll craft a response based on the tool execution
                if tool_calls_metadata:
                    first_tool = tool_calls_metadata[0]

                    if first_tool["tool"] == "add_task":
                        task_title = first_tool["result"]["title"]
                        response_text = f"I've added '{task_title}' to your task list."

                    elif first_tool["tool"] == "list_tasks":
                        tasks = first_tool["result"]["tasks"]
                        count = first_tool["result"]["count"]
                        status_filter = first_tool["parameters"].get("status", "all")

                        if count == 0:
                            if status_filter == "completed":
                                response_text = "You haven't completed any tasks yet."
                            elif status_filter == "pending":
                                response_text = "Your task list is empty! You're all caught up."
                            else:
                                response_text = "Your task list is empty! Add some tasks to get started."
                        else:
                            # Format task list
                            status_label = "" if status_filter == "all" else f" {status_filter}"
                            response_text = f"Here are your{status_label} tasks:\n\n"

                            for task in tasks:
                                checkbox = "✅" if task["completed"] else "⬜"
                                response_text += f"{checkbox} {task['title']}\n"
                                if task["description"]:
                                    response_text += f"   📝 {task['description']}\n"

                            response_text += f"\n({count} task{'s' if count != 1 else ''})"

                    elif first_tool["tool"] == "complete_task":
                        task_title = first_tool["result"]["title"]
                        status = first_tool["result"]["status"]
                        if status == "completed":
                            response_text = f"✅ Great! I've marked '{task_title}' as complete."
                        else:
                            response_text = f"I've marked '{task_title}' as incomplete."

                    elif first_tool["tool"] == "update_task":
                        task_title = first_tool["result"]["title"]
                        response_text = f"I've updated the task to '{task_title}'."

                    elif first_tool["tool"] == "delete_task":
                        task_title = first_tool["result"]["title"]
                        response_text = f"I've deleted '{task_title}' from your list."

                    else:
                        response_text = assistant_message.content or "Operation completed successfully."
                else:
                    response_text = assistant_message.content or "Operation completed successfully."
            else:
                # No tool calls, use assistant's direct response
                response_text = assistant_message.content or ""

            return {
                "response": response_text,
                "tool_calls": tool_calls_metadata,
            }

        except Exception as e:
            # Log error and return user-friendly message
            print(f"Agent error: {str(e)}")
            return {
                "response": "I'm having trouble processing your request right now. Please try again.",
                "tool_calls": [],
            }
