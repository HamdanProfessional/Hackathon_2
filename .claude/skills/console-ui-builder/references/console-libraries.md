# Console UI Resources

## Libraries

### Rich (Display Library)
- **Website**: https://rich.readthedocs.io/
- **Best for**: Tables, progress bars, syntax highlighting, panels
- **Pros**: Easy to use, beautiful output, great for CLI tools
- **Install**: `pip install rich`

### Textual (TUI Framework)
- **Website**: https://textual.textual.io/
- **Best for**: Full terminal UI applications (like htop)
- **Pros**: Modern, async, powerful widget system
- **Install**: `pip install textual`

### Prompt Toolkit (Interactive)
- **Website**: https://python-prompt-toolkit.readthedocs.io/
- **Best for**: Interactive prompts, autocompletion, multi-line input
- **Pros**: Rich input handling, IDE-like features
- **Install**: `pip install prompt-toolkit`

### blessed (Curses Wrapper)
- **Website**: https://blessed.readthedocs.io/
- **Best for**: Low-level terminal control
- **Pros**: Cross-platform, simple API
- **Install**: `pip install blessed`

## Common Patterns

### Progress with Rich
```python
from rich.progress import Progress
import time

with Progress() as progress:
    task1 = progress.add_task("Downloading...", total=100)
    task2 = progress.add_task("Processing...", total=100)
    while not progress.finished:
        progress.update(task1, advance=1)
        progress.update(task2, advance=2)
        time.sleep(0.05)
```

### Syntax Highlighting
```python
from rich.syntax import Syntax
from rich.console import Console

code = '''
def hello():
    print("Hello, World!")
'''

console = Console()
syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
console.print(syntax)
```

### Spinners
```python
from rich.console import Console
from time import sleep

console = Console()

with console.status("[bold green]Loading...") as status:
    while True:
        sleep(1)
        status.update("Loading... [processing]")
```
