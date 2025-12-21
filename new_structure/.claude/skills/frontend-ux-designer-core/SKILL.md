---
name: frontend-ux-designer-core
description: Complete frontend and UX development for Next.js applications with ChatKit integration. Handles React components, Tailwind CSS styling, TypeScript interfaces, console UI creation, and seamless chat interface implementation. Manages UI evolution from CLI to web to AI chatbot interfaces across all phases.
---

# Frontend UX Designer Core

## Quick Start

```typescript
// Generate complete frontend
import { FrontendScaffold } from 'frontend-ux-designer-core';

const scaffold = new FrontendScaffold({
  framework: 'nextjs',
  ui: 'tailwind',
  features: ['auth', 'tasks', 'chat']
});

scaffold.generate();

// Output:
// - Next.js App Router structure
// - React components with TypeScript
// - Tailwind CSS styling
// - ChatKit integration
```

## Core Capabilities

### 1. Next.js App Router Components
```typescript
// Page component with App Router
export default function TasksPage() {
  return (
    <div className="container mx-auto p-4">
      <TaskHeader />
      <TaskForm onSubmit={handleAddTask} />
      <TaskList tasks={tasks} />
    </div>
  );
}
```

### 2. ChatKit Integration
```typescript
// Chat interface for Phase III
import { ChatKitProvider, ChatView } from '@openai/chatkit-react';

export function TodoChat() {
  return (
    <ChatKitProvider
      apiUrl="/api/chat"
      authToken={userToken}
      theme="todo-theme"
    >
      <ChatView
        welcomeMessage="Hi! I can help you manage your tasks."
        placeholder="Ask me to add or complete tasks..."
      />
    </ChatKitProvider>
  );
}
```

### 3. Console UI (Rich Library)
```python
# Phase I console interface
from rich.console import Console
from rich.table import Table

def display_tasks(tasks):
    console = Console()
    table = Table(title="Tasks")

    table.add_column("ID", style="cyan")
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")

    for task in tasks:
        status = "✓" if task.completed else "✗"
        table.add_row(str(task.id), task.title, status)

    console.print(table)
```

## Phase Evolution

### Phase I: Console UI (Rich/Textual)
```python
# Rich console components
class TaskConsoleUI:
    def show_menu(self):
        console.print("[bold cyan]Todo Menu[/bold cyan]")
        console.print("1. Add Task")
        console.print("2. List Tasks")
        console.print("3. Complete Task")

    def get_input(self, prompt: str) -> str:
        return Prompt.ask(prompt)
```

### Phase II: Web UI (Next.js + Tailwind)
```typescript
// React components
export function TaskItem({ task }: { task: Task }) {
  return (
    <div className="flex items-center justify-between p-4 border rounded-lg">
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => toggleComplete(task.id)}
          className="h-5 w-5"
        />
        <span className={task.completed ? 'line-through text-gray-500' : ''}>
          {task.title}
        </span>
      </div>
      <Button onClick={() => deleteTask(task.id)} variant="ghost">
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
```

### Phase III: Chat UI (ChatKit)
```typescript
// AI-powered interface
export function ChatInterface() {
  const { sendMessage, messages, isLoading } = useChat();

  return (
    <div className="flex flex-col h-full">
      <MessageList messages={messages} />
      <MessageInput
        onSend={sendMessage}
        placeholder="e.g., 'Add a task to buy groceries'"
        disabled={isLoading}
      />
    </div>
  );
}
```

## Component Library

### Base Components
```typescript
// Reusable UI primitives
export function Button({
  children,
  variant = "primary",
  size = "md",
  ...props
}) {
  const baseStyles = "rounded-lg font-medium transition-colors";
  const variants = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    ghost: "hover:bg-gray-100"
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

### Form Components
```typescript
// Form with validation
export function TaskForm({ onSubmit }: { onSubmit: (task: TaskCreate) => void }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onSubmit({ title: title.trim(), description: description.trim() });
      setTitle('');
      setDescription('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title..."
        required
      />
      <Textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)..."
        rows={3}
      />
      <Button type="submit" className="w-full">
        Add Task
      </Button>
    </form>
  );
}
```

## Responsive Design

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
        }
      },
      screens: {
        '3xl': '1600px',
      }
    },
  },
  plugins: [],
}
```

### Mobile-First Design
```typescript
// Responsive component
export function TaskGrid({ tasks }: { tasks: Task[] }) {
  return (
    <div className="grid gap-4
                    md:grid-cols-2
                    lg:grid-cols-3
                    xl:grid-cols-4">
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  );
}
```

## TypeScript Integration

### Type Definitions
```typescript
// Shared types with backend
interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface User {
  id: string;
  email: string;
  name?: string;
}

// API response types
interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}
```

### API Client
```typescript
// Type-safe API client
class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  async getTasks(): Promise<Task[]> {
    const response = await fetch(`${this.baseUrl}/api/tasks`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
  }
}
```

## ChatKit Customization

### Theme Configuration
```typescript
// Custom ChatKit theme
const todoTheme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#64748b',
    background: '#ffffff',
    userMessage: '#3b82f6',
    assistantMessage: '#f1f5f9',
  },
  typography: {
    fontFamily: 'Inter, sans-serif',
  },
};
```

### Custom Components
```typescript
// Custom message component for task updates
const TaskUpdateMessage = ({ toolCall }: { toolCall: ToolCall }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
      <h4 className="font-medium text-green-900">Task Updated</h4>
      <p className="text-green-700">{toolCall.result.message}</p>
    </div>
  );
};
```

## Console UI Patterns

### Interactive Forms
```python
# Rich form for task creation
def task_creation_form():
    console.print("\n[bold]Create New Task[/bold]\n")

    title = Prompt.ask("Task title", console=console)
    description = Prompt.ask("Description", default="", show_default=False, console=console)
    priority = Prompt.ask(
        "Priority",
        choices=["low", "medium", "high"],
        default="medium",
        console=console
    )

    return {
        'title': title,
        'description': description,
        'priority': priority
    }
```

### Progress Indicators
```python
# Progress tracking
def progress_with_steps(steps: List[str]):
    with Progress() as progress:
        task = progress.add_task("Processing...", total=len(steps))

        for step in steps:
            progress.update(task, description=step)
            time.sleep(0.5)
            progress.advance(task)
```

## Error Handling UI

### Error Boundaries
```typescript
// React error boundary
export function ErrorFallback({ error }: { error: Error }) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Something went wrong</h2>
        <p className="text-gray-600 mt-2">{error.message}</p>
        <Button onClick={() => window.location.reload()} className="mt-4">
          Reload Page
        </Button>
      </div>
    </div>
  );
}
```

### Loading States
```typescript
// Loading skeleton
export function TaskSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
      <div className="h-3 bg-gray-200 rounded w-1/2"></div>
    </div>
  );
}
```

## Accessibility

### ARIA Labels
```typescript
// Accessible task item
export function AccessibleTaskItem({ task }: { task: Task }) {
  return (
    <div
      role="article"
      aria-label={`Task: ${task.title}`}
      className="p-4 border rounded-lg"
    >
      <h3 className="font-medium">{task.title}</h3>
      <p className="text-sm text-gray-600">
        Status: <span aria-label={task.completed ? 'Completed' : 'Pending'}>
          {task.completed ? 'Completed' : 'Pending'}
        </span>
      </p>
    </div>
  );
}
```

### Keyboard Navigation
```typescript
// Keyboard shortcuts
export function KeyboardShortcuts() {
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'n') {
        // Focus new task input
        document.getElementById('new-task-input')?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, []);

  return null;
}
```

## Performance Optimization

### Code Splitting
```typescript
// Dynamic imports for large components
const TaskChart = dynamic(() => import('./TaskChart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false
});
```

### Image Optimization
```typescript
// Next.js Image component
import Image from 'next/image';

export function TaskImage({ src, alt }: { src: string; alt: string }) {
  return (
    <Image
      src={src}
      alt={alt}
      width={300}
      height={200}
      className="rounded-lg"
      priority={false}
    />
  );
}
```

## Testing UI Components

### Component Tests
```typescript
// React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskForm } from './TaskForm';

test('submits task with title', async () => {
  const onSubmit = jest.fn();
  render(<TaskForm onSubmit={onSubmit} />);

  fireEvent.change(screen.getByPlaceholderText('Task title'), {
    target: { value: 'Test task' }
  });
  fireEvent.click(screen.getByText('Add Task'));

  expect(onSubmit).toHaveBeenCalledWith({
    title: 'Test task',
    description: ''
  });
});
```

## Integration Points

### With Backend
- Type synchronization via shared TypeScript definitions
- API client generation from OpenAPI spec
- Real-time updates via WebSockets

### With AI Systems
- ChatKit theme customization
- Tool call visualization
- Conversation history display

### With Console UI
- Rich table displays
- Interactive forms
- Progress tracking

## Best Practices

### Component Design
1. **Single Responsibility** - Each component does one thing
2. **Props Interface** - Clear prop types with TypeScript
3. **Composition** - Build complex UI from simple components
4. **Accessibility** - WCAG compliance from start

### Performance
1. **Lazy Loading** - Load components when needed
2. **Memoization** - Prevent unnecessary re-renders
3. **Bundle Optimization** - Code splitting by route
4. **Image Optimization** - Use Next.js Image component

### UX Principles
1. **Consistent Design** - Follow design system
2. **Feedback** - Visual feedback for all actions
3. **Error Recovery** - Graceful error handling
4. **Progressive Enhancement** - Works without JavaScript