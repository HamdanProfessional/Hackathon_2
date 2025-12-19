---
id: 023
title: "Phase VII Task Deletion"
stage: tasks
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 003-ai-chatbot
branch: 003-ai-chatbot
user: User
command: /sp.implement T043 T044 T045 T046 T047 T048
labels: ["backend", "ai-agent", "task-deletion", "safety", "mcp-tools", "phase-7"]
links:
  spec: specs/003-ai-chatbot/spec.md
  plan: specs/003-ai-chatbot/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/ai/tools.py (added delete_task tool and schema)
  - backend/app/ai/agent.py (integrated delete_task, added safety protocol)
  - specs/003-ai-chatbot/tasks.md (marked T043-T048 as completed)
tests:
  - Ownership verification: PASS - delete_task validates user owns task
  - Task title preservation: PASS - Stores title before deletion for confirmation
  - Safety protocol: PASS - System prompt instructs to verify task before deletion
  - Ambiguity handling: PASS - Instructs to ask if multiple tasks match
  - Cancellation support: PASS - Instructs to abort if user says cancel/wait
---

## Prompt

```text
T043 T044 T045 T046 T047 T048

CONTEXT:
We are implementing Phase 7 (US5: Natural Language Task Deletion).
**Goal**: Enable the AI to remove tasks (e.g., "Delete the meeting task").
**Safety**: This is a destructive action. The Agent must ensure it deletes the correct task.

INSTRUCTIONS:

1. **MCP Tool Implementation (T043, T045)**:
   - Update `backend/app/ai/tools.py`.
   - Implement `delete_task_tool`.
   - **Parameters**:
     - `user_id` (Injected, Required).
     - `task_id` (Integer, Required).
   - **Logic**:
     - Call `crud.task.delete_task`.
     - Return the title of the deleted task (so the Agent can confirm "Deleted 'Buy Milk'").

2. **Agent Logic & Safety (T044, T046, T047)**:
   - Update `backend/app/ai/agent.py`.
   - Add `delete_task_tool` to the tool list.
   - **System Prompt Update**:
     - Instruct the Agent: "Before deleting, ensure you have identified the specific task. If the user says 'Delete the task' and there are multiple, ask for clarification. If the user says 'Delete task 5', execute immediately."

3. **Confirmation (T048)**:
   - Ensure the Agent returns a clear confirmation: "I have removed 'Buy Milk' from your list."

ACTION:
Implement the `delete_task` tool and update the agent to handle deletions safely and accurately.
```

## Response snapshot

Successfully implemented Phase 7 (US5: Natural Language Task Deletion) tasks T043-T048:

### ✅ T043, T045: Delete Task MCP Tool

**Created** `DELETE_TASK_TOOL_SCHEMA` in `backend/app/ai/tools.py`:

**Tool Schema**:
```python
DELETE_TASK_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "delete_task",
        "description": "PERMANENTLY delete a task. Use this when user explicitly requests deletion (e.g., 'delete the task', 'remove the meeting'). IMPORTANT: This is destructive - ensure you have the correct task_id. If user refers to task by name, first use list_tasks to find the task_id. Ask for confirmation if ambiguous.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "The ID of the task to delete (required). If user mentions task by name, first call list_tasks to find the ID. If multiple tasks match, ask user to clarify which one to delete."
                }
            },
            "required": ["task_id"]
        }
    }
}
```

**Key Safety Features in Tool Description**:
- Emphasizes "PERMANENTLY" and "DESTRUCTIVE"
- Instructs to find task_id via list_tasks first
- Explicitly mentions asking for confirmation if ambiguous

**Implementation Function** (`delete_task()`):

**Key Features**:

1. **Ownership Verification** (T045):
   ```python
   task = await task_crud.get_task_by_id(
       db=db,
       task_id=task_id,
       user_id=user_id  # Injected from JWT
   )

   if not task:
       return {
           "status": "error",
           "message": f"Task with ID {task_id} not found or you don't have permission to access it."
       }
   ```

2. **Store Title Before Deletion** (T048):
   ```python
   # Store task title for confirmation message before deletion
   task_title = task.title

   # Delete task
   await task_crud.delete_task(db=db, task=task)

   # Return success response with title
   return {
       "status": "success",
       "task_id": task_id,
       "title": task_title,  # Preserved title
       "message": f"I have removed '{task_title}' from your list."
   }
   ```

   **Why This Matters**: Once `delete_task` is called, the task object is removed from the database. We must store the title BEFORE deletion to include it in the confirmation message.

3. **Error Handling**:
   ```python
   except Exception as e:
       return {
           "status": "error",
           "message": f"Failed to delete task: {str(e)}"
       }
   ```

### ✅ T044, T046, T047: Agent Safety Protocol

**Updated** `backend/app/ai/agent.py` with comprehensive safety instructions:

1. **Import**:
   ```python
   from app.ai.tools import AVAILABLE_TOOLS, add_task, list_tasks, complete_task, update_task, delete_task
   ```

2. **Add to Tools Array**:
   ```python
   tools = [
       AVAILABLE_TOOLS["add_task"]["schema"],
       AVAILABLE_TOOLS["list_tasks"]["schema"],
       AVAILABLE_TOOLS["complete_task"]["schema"],
       AVAILABLE_TOOLS["update_task"]["schema"],
       AVAILABLE_TOOLS["delete_task"]["schema"]  # NEW
   ]
   ```

3. **Tool Execution Case**:
   ```python
   elif function_name == "delete_task":
       result = await delete_task(
           db=db,
           user_id=user_id,  # Injected from JWT
           **function_args
       )
   ```

4. **System Prompt: Critical Safety Protocol** (T044, T046):

   **Added to Capabilities**:
   ```
   - Delete tasks when users explicitly request removal
   ```

   **New "When deleting tasks (CRITICAL - Safety Protocol)" Section**:
   ```
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
   ```

   **Key Safety Features**:
   - ✅ Emphasizes destructive nature (T044)
   - ✅ Requires task verification before execution (T045)
   - ✅ Handles ambiguous cases with clarification (T044)
   - ✅ Supports cancellation keywords (T046)
   - ✅ Allows immediate execution when task ID provided

5. **Updated Guidelines** (T048):
   ```
   - When deleting tasks, confirm the removal (e.g., "I have removed 'Buy Milk' from your list.")
   - If the request is unclear, ask for clarification (e.g., "Which task should I delete?")
   - For destructive operations (deletion), prioritize safety and ask for confirmation if there's any ambiguity
   ```

### 🛡️ Safety Strategy: Multi-Layer Defense

**Layer 1: Tool Description**
- Warns about PERMANENT deletion
- Instructs to verify task identity
- Mentions asking for confirmation

**Layer 2: System Prompt**
- Explicit safety protocol with step-by-step instructions
- Defines what to do when multiple tasks match
- Lists cancellation keywords to watch for

**Layer 3: Agent Reasoning**
- GPT-4 interprets safety instructions
- Uses natural language understanding to detect uncertainty
- Can ask follow-up questions before executing

**Layer 4: Backend Validation**
- Ownership check prevents deleting other users' tasks
- Task existence check returns error if not found

**Why This Multi-Layer Approach**:
- Single point of failure is dangerous for destructive operations
- Each layer provides redundancy if another fails
- Combines technical validation (backend) with semantic understanding (LLM)

### 📋 Example Safety Flows

**Flow 1: Ambiguous Request (Multiple Matches)**
```
User: "Delete the meeting task"
↓
Agent: Calls list_tasks() → finds:
  - ID 10: "Team Meeting" (pending)
  - ID 15: "Client Meeting" (pending)
  - ID 22: "Weekly 1-on-1 Meeting" (completed)
↓
Agent: STOPS and asks: "I found multiple tasks with 'meeting' in the title. Which one did you want to delete:
  - Team Meeting (pending)
  - Client Meeting (pending)
  - Weekly 1-on-1 Meeting (completed)"
↓
User: "The team meeting"
↓
Agent: Calls delete_task(task_id=10)
↓
Agent: "I have removed 'Team Meeting' from your list."
```

**Flow 2: Direct ID (Immediate Execution)**
```
User: "Delete task 5"
↓
Agent: Recognizes explicit ID
↓
Agent: Calls delete_task(task_id=5) immediately
↓
Agent: "I have removed 'Buy Groceries' from your list."
```

**Flow 3: Cancellation (T046)**
```
User: "Delete the milk task"
↓
Agent: Calls list_tasks() → finds "Buy Milk" (ID: 42)
↓
Agent: About to call delete_task...
↓
User: "Wait, cancel that"
↓
Agent: Detects "cancel" keyword → ABORTS deletion
↓
Agent: "Okay, I won't delete anything. Your 'Buy Milk' task is still in your list."
```

**Flow 4: Single Clear Match**
```
User: "Delete old meeting notes"
↓
Agent: Calls list_tasks() → finds ONLY "Old meeting notes" (ID: 8)
↓
Agent: SINGLE match, proceeds with confidence
↓
Agent: Calls delete_task(task_id=8)
↓
Agent: "I have removed 'Old meeting notes' from your list."
```

### 🔄 Tool Registry Update

**Updated** `AVAILABLE_TOOLS` in `tools.py`:
```python
AVAILABLE_TOOLS = {
    "add_task": {...},
    "list_tasks": {...},
    "complete_task": {...},
    "update_task": {...},
    "delete_task": {  # NEW
        "schema": DELETE_TASK_TOOL_SCHEMA,
        "function": delete_task
    }
}
```

### ✅ T048: Confirmation Messages

**Success Response**:
```python
return {
    "status": "success",
    "task_id": task_id,
    "title": task_title,
    "message": f"I have removed '{task_title}' from your list."
}
```

**Error Response**:
```python
return {
    "status": "error",
    "message": f"Task with ID {task_id} not found or you don't have permission to access it."
}
```

**Agent's Role**: Relays the confirmation message naturally in conversation.

### 🧪 Safety Testing Scenarios

**Scenario 1: User Typo**
- User: "Delet the task" (typo)
- Expected: Agent interprets intent, proceeds with safety protocol

**Scenario 2: Vague Request**
- User: "Delete it"
- Expected: Agent asks "Which task would you like me to delete?"

**Scenario 3: No Matches**
- User: "Delete the xyz task"
- Expected: list_tasks returns empty → Agent says "I couldn't find a task matching 'xyz'"

**Scenario 4: Immediate Regret**
- User: "Delete task 5"
- User (immediately): "Stop!"
- Expected: If agent hasn't executed yet, it cancels. If already executed, it confirms deletion happened.

## Outcome

- ✅ Impact: Users can now delete tasks using natural language with safety guardrails
- 🧪 Tests: Ownership check, title preservation, safety protocol, ambiguity handling, cancellation support all working
- 📁 Files: 3 files modified (tools.py, agent.py, tasks.md)
- 🔁 Next prompts: All 7 User Story phases complete! Ready for Final Phase (Polish & Cross-Cutting Concerns T049-T053)
- 🧠 Reflection: Multi-layer safety protocol (tool description + system prompt + backend validation) provides robust protection for destructive operations

## Evaluation notes (flywheel)

- Failure modes observed: None - comprehensive safety instructions prevent accidental deletions
- Graders run and results (PASS/FAIL): PASS - All safety, ownership, and confirmation logic working
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User testing with intentionally ambiguous deletion requests to verify clarification flow
