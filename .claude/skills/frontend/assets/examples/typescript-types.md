# TypeScript Types Example

```typescript
// types/task.ts
export interface Task {
  id: number
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
  user_id: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}

export interface TaskListResponse {
  tasks: Task[]
  total: number
  page: number
  limit: number
}

// API Client Types
export interface ApiClient {
  getTasks(): Promise<Task[]>
  getTask(id: number): Promise<Task>
  createTask(task: TaskCreate): Promise<Task>
  updateTask(id: number, task: TaskUpdate): Promise<Task>
  deleteTask(id: number): Promise<void>
}
```

## Type Guards

```typescript
export function isTask(obj: unknown): obj is Task {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'id' in obj &&
    'title' in obj &&
    'completed' in obj
  )
}

export function hasDescription(task: Task): task is Task & { description: string } {
  return !!task.description
}
```
