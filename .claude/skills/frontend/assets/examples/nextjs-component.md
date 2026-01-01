# Next.js Component Example

## Server Component

```typescript
// app/components/task-list.tsx
import { Task } from '@/types/task'

interface TaskListProps {
  tasks: Task[]
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export default async function TaskList({
  tasks,
  onToggle,
  onDelete
}: TaskListProps) {
  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="flex items-center justify-between p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => onToggle(task.id)}
              className="w-5 h-5 rounded"
            />
            <div>
              <h3 className={task.completed ? 'line-through text-gray-500' : ''}>
                {task.title}
              </h3>
              {task.description && (
                <p className="text-sm text-gray-600">{task.description}</p>
              )}
            </div>
          </div>
          <button
            onClick={() => onDelete(task.id)}
            className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
          >
            Delete
          </button>
        </div>
      ))}
    </div>
  )
}
```

## Client Component with Hooks

```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

interface TaskFormProps {
  onSubmit: (task: { title: string; description: string }) => Promise<void>
}

export default function TaskForm({ onSubmit }: TaskFormProps) {
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await onSubmit({ title, description })
      router.push('/tasks')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Task Title
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          rows={3}
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  )
}
```
