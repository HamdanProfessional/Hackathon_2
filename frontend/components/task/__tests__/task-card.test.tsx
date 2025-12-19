import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TaskCard from '../task-card'
import { toast } from 'sonner'

// Mock the toast library
jest.mock('sonner', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}))

// Mock the apiClient
const mockDeleteTask = jest.fn()
jest.mock('@/lib/api', () => ({
  apiClient: {
    deleteTask: mockDeleteTask,
    updateTask: jest.fn(),
  },
}))

// Mock the useRouter
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}))

describe('TaskCard', () => {
  const user = userEvent.setup()
  const mockTask = {
    id: 1,
    title: 'Test Task',
    description: 'Test description',
    completed: false,
    priority: 'high',
    due_date: '2025-12-20',
    created_at: '2025-12-17T10:00:00Z',
    updated_at: '2025-12-17T10:00:00Z',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders task information correctly', () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    expect(screen.getByText('Test Task')).toBeInTheDocument()
    expect(screen.getByText('Test description')).toBeInTheDocument()
    expect(screen.getByTestId('priority-badge')).toBeInTheDocument()
  })

  it('shows completed state correctly', () => {
    const completedTask = { ...mockTask, completed: true }
    render(<TaskCard task={completedTask} onTaskUpdate={jest.fn()} />)

    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).toBeChecked()
  })

  it('shows incomplete state correctly', () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).not.toBeChecked()
  })

  it('calls onTaskUpdate when checkbox is clicked', async () => {
    const mockOnTaskUpdate = jest.fn()
    mockOnTaskUpdate.mockResolvedValue({ ...mockTask, completed: true })

    render(<TaskCard task={mockTask} onTaskUpdate={mockOnTaskUpdate} />)

    const checkbox = screen.getByRole('checkbox')
    await user.click(checkbox)

    await waitFor(() => {
      expect(mockOnTaskUpdate).toHaveBeenCalledWith(mockTask.id, !mockTask.completed)
    })
  })

  it('opens edit dialog when edit button is clicked', async () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    const editButton = screen.getByRole('button', { name: /edit task/i })
    await user.click(editButton)

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  it('opens delete dialog when delete button is clicked', async () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    const deleteButton = screen.getByRole('button', { name: /delete task/i })
    await user.click(deleteButton)

    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument()
    })
  })

  it('truncates long task titles', () => {
    const longTitleTask = {
      ...mockTask,
      title: 'This is a very long task title that should be truncated when displayed',
    }

    render(<TaskCard task={longTitleTask} onTaskUpdate={jest.fn()} />)

    const titleElement = screen.getByTestId('task-title')
    expect(titleElement).toHaveClass('line-clamp-2')
  })

  it('displays due date when present', () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    expect(screen.getByText(/2025-12-20/)).toBeInTheDocument()
  })

  it('does not display due date when not present', () => {
    const taskWithoutDueDate = { ...mockTask, due_date: null }

    render(<TaskCard task={taskWithoutDueDate} onTaskUpdate={jest.fn()} />)

    expect(screen.queryByText(/\d{4}-\d{2}-\d{2}/)).not.toBeInTheDocument()
  })

  it('applies correct priority styling', () => {
    render(<TaskCard task={mockTask} onTaskUpdate={jest.fn()} />)

    const priorityBadge = screen.getByTestId('priority-badge')
    expect(priorityBadge).toHaveAttribute('data-priority', 'high')
  })

  it('shows loading state when updating', async () => {
    const mockOnTaskUpdate = jest.fn()
    mockOnTaskUpdate.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<TaskCard task={mockTask} onTaskUpdate={mockOnTaskUpdate} />)

    const checkbox = screen.getByRole('checkbox')
    await user.click(checkbox)

    // Should show loading state on checkbox
    expect(checkbox).toBeDisabled()
  })

  it('handles update errors gracefully', async () => {
    const mockOnTaskUpdate = jest.fn()
    mockOnTaskUpdate.mockRejectedValue(new Error('Update failed'))

    render(<TaskCard task={mockTask} onTaskUpdate={mockOnTaskUpdate} />)

    const checkbox = screen.getByRole('checkbox')
    await user.click(checkbox)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to update task')
    })
  })
})