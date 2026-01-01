# Textual TUI Example

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, Button, ListView, ListItem
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive

class TodoApp(App):
    """A Todo TUI application."""
    CSS_PATH = "todo.css"
    TITLE = "Todo TUI"

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static("Add a new task:", classes="label")
            yield Input(placeholder="Task description...", id="task_input")
            with Horizontal():
                yield Button("Add", variant="primary", id="add_btn")
                yield Button("Complete", variant="success", id="complete_btn")
                yield Button("Delete", variant="error", id="delete_btn")
            yield Static("Tasks:", classes="label")
            yield ListView(id="task_list")
        yield Footer()

    def on_mount(self) -> None:
        self.task_list = self.query_one("#task_list", ListView)
        self.task_input = self.query_one("#task_input", Input)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add_btn":
            task_text = self.task_input.value
            if task_text:
                self.task_list.add(ListItem(task_text))
                self.task_input.value = ""

if __name__ == "__main__":
    app = TodoApp()
    app.run()
```

## CSS (todo.css)
```css
Screen {
    background: #1a1a1a;
}

Label {
    text-style: bold;
    color: #50fa7b;
    margin: 1 0;
}

#task_input {
    dock: top;
    margin: 1 0;
}

Horizontal {
    height: 3;
    margin: 1 0;
}

Button {
    margin: 0 1;
}

ListView {
    height: 1fr;
    border: thick #50fa7b;
}
```
