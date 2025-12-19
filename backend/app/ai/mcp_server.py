"""
MCP (Model Context Protocol) Server Implementation

This module wraps existing CRUD functions as MCP tools.
The MCP server exposes todo operations to the OpenAI Agent.

Security: All tools require user_id parameter to prevent cross-user access.

Tools:
- add_task: Create new task
- list_tasks: Get all tasks (with filtering)
- complete_task: Mark task as complete
- update_task: Update task fields
- delete_task: Delete task

References:
- MCP Python SDK: https://modelcontextprotocol.io/docs/sdk
"""

from typing import Dict, List, Optional


class TodoMCPServer:
    """
    MCP server exposing todo CRUD operations as tools.

    Each tool:
    1. Receives user_id from security wrapper (injected)
    2. Calls existing CRUD function from app.crud.task
    3. Returns structured response for Agent
    """

    def __init__(self):
        """Initialize MCP server and register tools."""
        # TODO: Initialize Server from MCP SDK
        # self.server = Server("todo-mcp-server")
        # self._register_tools()

    def _register_tools(self):
        """
        Register all MCP tools.

        Each tool is decorated with @self.server.tool()
        to expose it to the Agent.
        """
        # TODO: Implement tool registration in Phase 3
        pass

    async def add_task(
        self,
        user_id: int,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> Dict:
        """
        MCP Tool: Create a new task.

        Args:
            user_id: User ID (injected by security wrapper)
            title: Task title (required)
            description: Task description (optional)
            priority: low | medium | high (default: medium)
            due_date: ISO format date string (optional)

        Returns:
            {"task_id": int, "status": "created", "title": str}
        """
        # TODO: Implement with task_crud.create_task
        raise NotImplementedError("Tool implementation pending Phase 3")

    async def list_tasks(
        self,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Dict:
        """
        MCP Tool: List all tasks for user.

        Args:
            user_id: User ID (injected by security wrapper)
            status: Filter by PENDING | COMPLETED (optional)
            priority: Filter by low | medium | high (optional)

        Returns:
            {"tasks": List[dict], "count": int}
        """
        # TODO: Implement with task_crud.get_tasks
        raise NotImplementedError("Tool implementation pending Phase 4")

    async def complete_task(self, user_id: int, task_id: int) -> Dict:
        """
        MCP Tool: Mark task as complete.

        Args:
            user_id: User ID (injected by security wrapper)
            task_id: Task ID to complete

        Returns:
            {"task_id": int, "status": "completed"}
        """
        # TODO: Implement with task_crud.update_task
        raise NotImplementedError("Tool implementation pending Phase 5")

    async def update_task(
        self,
        user_id: int,
        task_id: int,
        **fields
    ) -> Dict:
        """
        MCP Tool: Update task fields.

        Args:
            user_id: User ID (injected by security wrapper)
            task_id: Task ID to update
            **fields: Fields to update (title, description, priority, due_date)

        Returns:
            {"task_id": int, "status": "updated", "fields": List[str]}
        """
        # TODO: Implement with task_crud.update_task
        raise NotImplementedError("Tool implementation pending Phase 6")

    async def delete_task(self, user_id: int, task_id: int) -> Dict:
        """
        MCP Tool: Delete task.

        Args:
            user_id: User ID (injected by security wrapper)
            task_id: Task ID to delete

        Returns:
            {"task_id": int, "status": "deleted"}
        """
        # TODO: Implement with task_crud.delete_task
        raise NotImplementedError("Tool implementation pending Phase 7")
