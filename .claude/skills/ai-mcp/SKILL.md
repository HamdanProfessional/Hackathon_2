---
name: mcp-builder
description: Convert slash commands from .claude/commands/ into a fully functional MCP (Model Context Protocol) server using the Official MCP SDK. Use when Claude needs to create reusable spec-driven workflows across all AI development tools, or when users want to expose their custom commands as MCP prompts for use in any MCP-compatible IDE.
license: Complete terms in LICENSE.txt
---

# MCP Builder

Converts slash commands into MCP server for cross-IDE compatibility.

## Quick Start

Create MCP server from commands:
```bash
/skill mcp-builder
```

Or via Task tool:
```python
Task(
    subagent_type="mcp-builder",
    description="Build MCP server from commands",
    prompt="Create an MCP server that exposes all .claude/commands as prompts"
)
```

## Implementation Steps

### 1. Analyze Commands
Scan `.claude/commands/` directory and extract:
- Command structure and parameters
- Prompt templates and variables
- Dependencies between commands

### 2. Generate Server
Create `mcp-server/server.py` with:
- FastMCP instance initialization
- `@mcp.prompt()` function for each command
- Parameter validation and error handling

### 3. Configure Integration
- Generate `.mcp.json` configuration
- Set up environment variables
- Create package configuration

### 4. Test & Document
- Validate server starts and prompts work
- Create README with usage instructions

## Generated Structure

```
mcp-server/
├── server.py          # MCP server implementation
├── pyproject.toml      # Package configuration
└── README.md          # Usage documentation
.mcp.json              # MCP client configuration
```

## Command Mapping

| Slash Command | MCP Prompt | Parameters |
|---------------|------------|------------|
| `/sp.specify` | `sp_specify` | feature_name, description |
| `/sp.plan` | `sp_plan` | feature_name |
| `/sp.tasks` | `sp_tasks` | feature_name |
| `/sp.implement` | `sp_implement` | feature_name, task_ids |

## Example MCP Prompt

```python
@mcp.prompt()
async def sp_specify(feature_name: str, description: str = "") -> str:
    """Create feature specification using Spec-Kit template."""
    return f"""
    Create specs/{feature_name}/spec.md with:
    - Feature requirements
    - Acceptance criteria
    - User stories
    Description: {description}
    """
```

## Benefits

- Cross-IDE compatibility (Claude, VS Code, Cursor, etc.)
- Standardized development workflow
- Reusable intelligence across tools
- +200 hackathon bonus points

## Error Handling

- Parse errors: Log and continue with other commands
- Server startup: Verify Python 3.10+ and MCP SDK
- Prompt failures: Validate parameters and return helpful errors