import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TaskForm from '../task-form'
import { toast } from 'sonner'

// Mock the toast library
jest.mock('sonner', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}))

// Mock the apiClient
const mockCreateTask = jest.fn()
const mockUpdateTask = jest.fn()
jest.mock('@/lib/api', () => ({
  apiClient: {
    createTask: mockCreateTask,
    updateTask: mockUpdateTask,
  },
}))

describe('TaskForm', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders form fields for new task', () => {
    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    expect(screen.getByLabelText(/task title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/due date/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument()
  })

  it('renders form fields for editing task', () => {
    const existingTask = {
      id: 1,
      title: 'Existing Task',
      description: 'Existing description',
      priority: 'medium',
      due_date: '2025-12-20',
      completed: false,
    }

    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} task={existingTask} />)

    expect(screen.getByDisplayValue('Existing Task')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Existing description')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /update task/i })).toBeInTheDocument()
  })

  it('shows validation error for empty title', async () => {
    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    const createButton = screen.getByRole('button', { name: /create task/i })
    await user.click(createButton)

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for title that exceeds 500 characters', async () => {
    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const longTitle = 'A'.repeat(501)
    await user.type(titleInput, longTitle)
    await user.tab()

    await waitFor(() => {
      expect(screen.getByText(/title must be less than 500 characters/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data for new task', async () => {
    const mockOnTaskCreated = jest.fn()
    const mockNewTask = {
      id: 1,
      title: 'New Task',
      description: 'New description',
      priority: 'high',
      due_date: '2025-12-20',
      completed: false,
    }
    mockCreateTask.mockResolvedValue(mockNewTask)

    render(<TaskForm onClose={jest.fn()} onTaskCreated={mockOnTaskCreated} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const prioritySelect = screen.getByLabelText(/priority/i)
    const dueDateInput = screen.getByLabelText(/due date/i)
    const createButton = screen.getByRole('button', { name: /create task/i })

    await user.type(titleInput, 'New Task')
    await user.type(descriptionInput, 'New description')
    await user.selectOptions(prioritySelect, 'high')
    await user.type(dueDateInput, '2025-12-20')
    await user.click(createButton)

    await waitFor(() => {
      expect(mockCreateTask).toHaveBeenCalledWith({
        title: 'New Task',
        description: 'New description',
        priority: 'high',
        due_date: '2025-12-20',
      })
    })

    await waitFor(() => {
      expect(mockOnTaskCreated).toHaveBeenCalledWith(mockNewTask)
    })

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Task created successfully')
    })
  })

  it('submits form with valid data for editing task', async () => {
    const existingTask = {
      id: 1,
      title: 'Old Title',
      description: 'Old description',
      priority: 'low',
      due_date: '2025-12-15',
      completed: false,
    }

    const mockUpdatedTask = {
      ...existingTask,
      title: 'Updated Title',
      description: 'Updated description',
      priority: 'high',
      due_date: '2025-12-20',
    }
    mockUpdateTask.mockResolvedValue(mockUpdatedTask)

    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} task={existingTask} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const prioritySelect = screen.getByLabelText(/priority/i)
    const dueDateInput = screen.getByLabelText(/due date/i)
    const updateButton = screen.getByRole('button', { name: /update task/i })

    await user.clear(titleInput)
    await user.type(titleInput, 'Updated Title')
    await user.clear(descriptionInput)
    await user.type(descriptionInput, 'Updated description')
    await user.selectOptions(prioritySelect, 'high')
    await user.clear(dueDateInput)
    await user.type(dueDateInput, '2025-12-20')
    await user.click(updateButton)

    await waitFor(() => {
      expect(mockUpdateTask).toHaveBeenCalledWith(existingTask.id, {
        title: 'Updated Title',
        description: 'Updated description',
        priority: 'high',
        due_date: '2025-12-20',
      })
    })

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith('Task updated successfully')
    })
  })

  it('shows error message on submit failure', async () => {
    mockCreateTask.mockRejectedValue(new Error('Network error'))

    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const createButton = screen.getByRole('button', { name: /create task/i })

    await user.type(titleInput, 'Test Task')
    await user.click(createButton)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to create task')
    })
  })

  it('calls onClose when cancel button is clicked', async () => {
    const mockOnClose = jest.fn()

    render(<TaskForm onClose={mockOnClose} onTaskCreated={jest.fn()} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('shows loading state during submission', async () => {
    mockCreateTask.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const createButton = screen.getByRole('button', { name: /create task/i })

    await user.type(titleInput, 'Test Task')
    await user.click(createButton)

    expect(screen.getByRole('button', { name: /creating.../i })).toBeInTheDocument()
    expect(createButton).toBeDisabled()
  })

  it('clears form on successful creation', async () => {
    const mockNewTask = {
      id: 1,
      title: 'Test Task',
      description: 'Test description',
      priority: 'medium',
      due_date: '2025-12-20',
      completed: false,
    }
    mockCreateTask.mockResolvedValue(mockNewTask)

    render(<TaskForm onClose={jest.fn()} onTaskCreated={jest.fn()} />)

    const titleInput = screen.getByLabelText(/task title/i)
    const descriptionInput = screen.getByLabelText(/description/i)
    const createButton = screen.getByRole('button', { name: /create task/i })

    await user.type(titleInput, 'Test Task')
    await user.type(descriptionInput, 'Test description')
    await user.click(createButton)

    await waitFor(() => {
      expect(screen.getByDisplayValue('')).toBeInTheDocument() // Title should be cleared
    })
  })
})