# MCP Builder Skill

**Type**: Agent Skill
**Category**: AI & MCP
**Phases**: All (especially Phase III+)

---

## Purpose

This skill converts slash commands from `.claude/commands/` into a fully functional MCP (Model Context Protocol) server using the Official MCP SDK. This creates reusable spec-driven workflows across all AI development tools.

---

## Skill Invocation

```
/skill mcp-builder
```

Or via Claude Code Task tool:
```python
Task(
    subagent_type="mcp-builder",
    description="Build MCP server from commands",
    prompt="Create an MCP server that exposes all .claude/commands as prompts"
)
```

---

## What This Skill Does

1. **Analyzes Slash Commands**
   - Scans `.claude/commands/` directory
   - Parses command structure
   - Extracts parameters and prompts
   - Identifies dependencies

2. **Generates MCP Server**
   - Creates Python MCP server using Official SDK
   - Converts commands to MCP prompts
   - Adds parameter validation
   - Implements error handling

3. **Creates Configuration**
   - Generates `.mcp.json` config
   - Sets up environment variables
   - Documents connection settings
   - Adds usage examples

4. **Tests MCP Server**
   - Validates server starts
   - Tests each prompt
   - Verifies parameter passing
   - Checks error handling

5. **Documents Integration**
   - README for MCP server
   - Connection instructions
   - Usage examples
   - Troubleshooting guide

---

## MCP Server Architecture

```
┌─────────────────────────────────────────────────┐
│           MCP Server (Python)                    │
│  ┌───────────────────────────────────────────┐  │
│  │  Official MCP SDK                         │  │
│  └───────────────┬───────────────────────────┘  │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐  │
│  │  Prompt Registry                          │  │
│  │  - sp.specify                             │  │
│  │  - sp.plan                                │  │
│  │  - sp.tasks                               │  │
│  │  - sp.implement                           │  │
│  │  - sp.clarify                             │  │
│  │  - sp.analyze                             │  │
│  │  - sp.checklist                           │  │
│  │  - sp.adr                                 │  │
│  │  - sp.phr                                 │  │
│  │  - sp.git.commit_pr                       │  │
│  └───────────────┬───────────────────────────┘  │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐  │
│  │  Command Processor                        │  │
│  │  - Parse parameters                       │  │
│  │  - Validate inputs                        │  │
│  │  - Execute command logic                  │  │
│  │  - Return formatted response              │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│     MCP Clients (Connect via .mcp.json)         │
│  - Claude Code                                  │
│  - VS Code (Copilot)                            │
│  - Cursor                                       │
│  - Windsurf                                     │
│  - Any MCP-compatible IDE                       │
└─────────────────────────────────────────────────┘
```

---

## Generated Files

### 1. MCP Server (`mcp-server/server.py`)

```python
"""
SpecKit Plus MCP Server
Exposes spec-driven development commands as MCP prompts
"""
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("speckit-plus")

@mcp.prompt()
async def sp_specify(feature_name: str, description: str = "") -> str:
    """
    Create a feature specification using the Spec-Kit Plus template.

    Args:
        feature_name: Name of the feature (e.g., 'todo-crud')
        description: Brief description of the feature

    Returns:
        Prompt to create the specification
    """
    return f"""
You are tasked with creating a feature specification for: {feature_name}

Description: {description}

Using the Spec-Kit Plus workflow:
1. Read the spec template from .specify/templates/spec-template.md
2. Read the constitution from .specify/memory/constitution.md
3. Create a new spec file at specs/{feature_name}/spec.md
4. Fill in all sections with detailed requirements
5. Ensure all acceptance criteria are testable

Focus on WHAT the feature does, not HOW it's implemented.
"""

@mcp.prompt()
async def sp_plan(feature_name: str) -> str:
    """
    Generate implementation plan for a feature.

    Args:
        feature_name: Name of the feature with existing spec

    Returns:
        Prompt to create the implementation plan
    """
    return f"""
You are tasked with creating an implementation plan for: {feature_name}

Using the Spec-Kit Plus workflow:
1. Read specs/{feature_name}/spec.md to understand requirements
2. Read .specify/memory/constitution.md for constraints
3. Read .specify/templates/plan-template.md for structure
4. Create specs/{feature_name}/plan.md with:
   - Component breakdown
   - Data structures
   - Interfaces
   - Error handling strategy
   - Constitution compliance check

Focus on HOW to implement, respecting current phase constraints.
"""

@mcp.prompt()
async def sp_tasks(feature_name: str) -> str:
    """
    Generate actionable task list for a feature.

    Args:
        feature_name: Name of the feature with existing spec and plan

    Returns:
        Prompt to create the task breakdown
    """
    return f"""
You are tasked with breaking down {feature_name} into actionable tasks.

Using the Spec-Kit Plus workflow:
1. Read specs/{feature_name}/spec.md for requirements
2. Read specs/{feature_name}/plan.md for architecture
3. Read .specify/templates/tasks-template.md for structure
4. Create specs/{feature_name}/tasks.md with:
   - Task IDs (T-001, T-002, etc.)
   - Clear descriptions
   - File paths to modify
   - Acceptance criteria
   - Dependencies

Each task should be atomic and independently testable.
"""

@mcp.prompt()
async def sp_implement(feature_name: str, task_ids: str = "all") -> str:
    """
    Execute implementation tasks for a feature.

    Args:
        feature_name: Name of the feature
        task_ids: Comma-separated task IDs or 'all'

    Returns:
        Prompt to implement the tasks
    """
    return f"""
You are tasked with implementing {feature_name}.

Tasks to implement: {task_ids}

Using the Spec-Kit Plus workflow:
1. Read specs/{feature_name}/tasks.md
2. Implement only the specified tasks
3. Reference Task IDs in code comments
4. Follow plan architecture exactly
5. Test each task before proceeding

Implement code ONLY as defined in tasks. No creative additions.
"""

# Add more prompts for other commands...

if __name__ == "__main__":
    mcp.run()
```

---

### 2. MCP Configuration (`.mcp.json`)

```json
{
  "mcpServers": {
    "speckit-plus": {
      "command": "python",
      "args": ["mcp-server/server.py"],
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  }
}
```

---

### 3. Package Configuration (`mcp-server/pyproject.toml`)

```toml
[project]
name = "speckit-plus-mcp"
version = "1.0.0"
description = "MCP server for Spec-Kit Plus spec-driven development"
dependencies = [
    "mcp>=0.9.0",
    "pydantic>=2.0.0"
]

[project.scripts]
speckit-mcp = "server:main"
```

---

### 4. README (`mcp-server/README.md`)

```markdown
# SpecKit Plus MCP Server

MCP server that exposes Spec-Kit Plus commands as prompts.

## Installation

```bash
cd mcp-server
pip install -e .
```

## Configuration

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "speckit-plus": {
      "command": "python",
      "args": ["mcp-server/server.py"]
    }
  }
}
```

## Available Prompts

- `sp_specify(feature_name, description)` - Create feature spec
- `sp_plan(feature_name)` - Generate implementation plan
- `sp_tasks(feature_name)` - Break down into tasks
- `sp_implement(feature_name, task_ids)` - Execute implementation

## Usage

From any MCP-compatible IDE:

```
@mcp sp_specify todo-crud "Basic CRUD operations for todo items"
```

## Testing

```bash
python server.py
```
```

---

## Conversion Mapping

### Slash Command → MCP Prompt

| Slash Command | MCP Prompt Function | Parameters |
|---------------|---------------------|------------|
| `/sp.specify` | `sp_specify()` | feature_name, description |
| `/sp.plan` | `sp_plan()` | feature_name |
| `/sp.tasks` | `sp_tasks()` | feature_name |
| `/sp.implement` | `sp_implement()` | feature_name, task_ids |
| `/sp.clarify` | `sp_clarify()` | feature_name |
| `/sp.analyze` | `sp_analyze()` | feature_name |
| `/sp.checklist` | `sp_checklist()` | feature_name |
| `/sp.adr` | `sp_adr()` | decision_title |
| `/sp.phr` | `sp_phr()` | title, stage |
| `/sp.git.commit_pr` | `sp_git_commit_pr()` | action |

---

## Implementation Steps

### Phase 1: Analysis
1. Scan `.claude/commands/*.md`
2. Parse each command file
3. Extract:
   - Command name
   - Description
   - Parameters
   - Prompt template
   - Variables

### Phase 2: Server Generation
1. Create `mcp-server/` directory
2. Generate `server.py` with:
   - MCP SDK imports
   - FastMCP instance
   - One `@mcp.prompt()` per command
   - Parameter validation
   - Error handling

### Phase 3: Configuration
1. Create `.mcp.json`
2. Set server command
3. Configure environment
4. Add startup script

### Phase 4: Testing
1. Start MCP server
2. Test each prompt
3. Verify parameter passing
4. Check error cases
5. Validate responses

### Phase 5: Documentation
1. Create README.md
2. Document installation
3. Add usage examples
4. Include troubleshooting

---

## Example Command Conversion

### Input: `.claude/commands/sp.specify.md`

```markdown
You are tasked with creating a feature specification.

Feature: {{FEATURE_NAME}}
Description: {{DESCRIPTION}}

Create specs/{{FEATURE_NAME}}/spec.md using the template...
```

### Output: MCP Prompt Function

```python
@mcp.prompt()
async def sp_specify(feature_name: str, description: str = "") -> str:
    """Create a feature specification using Spec-Kit Plus template."""
    return f"""
You are tasked with creating a feature specification.

Feature: {feature_name}
Description: {description}

Create specs/{feature_name}/spec.md using the template...
"""
```

---

## Benefits

### For Developers
- ✅ Use spec-driven workflow in any IDE
- ✅ Consistent prompts across tools
- ✅ No vendor lock-in
- ✅ Reusable intelligence

### For Teams
- ✅ Standardized development process
- ✅ Shared spec templates
- ✅ Cross-tool compatibility
- ✅ Easier onboarding

### For Hackathon
- ✅ +200 bonus points (Reusable Intelligence)
- ✅ Demonstrates advanced MCP usage
- ✅ Cloud-Native Blueprint potential
- ✅ Judges see innovation

---

## Success Criteria

MCP server is successful when:

1. ✅ Server starts without errors
2. ✅ All commands converted to prompts
3. ✅ Parameters validated correctly
4. ✅ Prompts return expected results
5. ✅ Works in multiple IDEs
6. ✅ Documentation complete
7. ✅ Tests passing

---

## Error Handling

### If Command Parse Fails
- Log which file failed
- Show parsing error
- Continue with other commands

### If Server Won't Start
- Check Python version (3.10+)
- Verify MCP SDK installed
- Check .mcp.json syntax

### If Prompt Fails
- Validate parameters
- Check template substitution
- Return helpful error message

---

## Deliverables

When this skill completes, you'll have:

1. ✅ `mcp-server/server.py` - MCP server implementation
2. ✅ `.mcp.json` - Configuration file
3. ✅ `mcp-server/pyproject.toml` - Package config
4. ✅ `mcp-server/README.md` - Documentation
5. ✅ Working MCP server exposing all commands
6. ✅ Integration instructions

---

**Skill Version**: 1.0.0
**Created**: 2025-12-13
**Hackathon Points**: Contributes to +200 bonus (Reusable Intelligence)
**Phase**: All (especially III+)
