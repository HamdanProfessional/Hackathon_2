# Evolution of TODO - Phase I: Console Application

A simple in-memory todo list manager with an interactive terminal interface.

## Features

- ✅ **Add Task** - Create tasks with title and optional description
- ✅ **View Tasks** - List all tasks with completion status
- ✅ **Update Task** - Modify task title and description
- ✅ **Delete Task** - Remove tasks from the list
- ✅ **Mark Complete** - Toggle task completion status

## Tech Stack

- **Python 3.13+** - Modern Python with type hints
- **Rich** - Beautiful terminal UI
- **UV** - Fast Python package manager

## Installation

### Using UV (Recommended)

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Or install in development mode
uv pip install -e .
```

### Using pip

```bash
pip install rich
```

## Usage

### Run the application

```bash
# Using UV
uv run python -m src

# Or if installed
todo
```

### Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `add` | `add <title> [-d <description>]` | Add a new task |
| `list` | `list` | List all tasks |
| `update` | `update <id> [-t <title>] [-d <desc>]` | Update a task |
| `delete` | `delete <id>` | Delete a task |
| `complete` | `complete <id>` | Mark task as complete |
| `uncomplete` | `uncomplete <id>` | Mark task as incomplete |
| `help` | `help` | Show available commands |
| `exit` | `exit` | Exit the application |

## Examples

```
todo> add Buy groceries -d Milk, eggs, and bread
✓ Task added: Buy groceries (ID: 1)

todo> add Complete project documentation
✓ Task added: Complete project documentation (ID: 2)

todo> list
┏━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Status ┃ Title                       ┃ Description        ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ ○ Todo │ Buy groceries                │ Milk, eggs, bread   │
│ 2  │ ○ Todo │ Complete project            │ documentation      │
└────┴────────┴─────────────────────────────┴────────────────────┘

Summary: 0/2 tasks completed

todo> complete 1
✓ Task marked as complete: Buy groceries (ID: 1)

todo> update 2 -t "Finish hackathon project"
✓ Task updated: Finish hackathon project (ID: 2)

todo> delete 1
✓ Task deleted: Buy groceries (ID: 1)

todo> exit
Goodbye! 👋
```

## Project Structure

```
src/
├── __init__.py       # Package initialization
├── __main__.py       # Entry point
├── cli.py            # Command-line interface
├── models.py         # Task data models
├── pyproject.toml    # Project configuration
└── README.md         # This file
```

## Development

### Running Tests

```bash
# Run with UV
uv run python -m src

# Run directly
python -m src
```

## License

MIT License - see LICENSE file for details.

---

**Phase I of Evolution of TODO - PIAIC Hackathon II**
