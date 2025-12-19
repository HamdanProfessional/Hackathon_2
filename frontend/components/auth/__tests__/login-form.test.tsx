import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { toast } from 'sonner'
import LoginForm from '../login-form'
import { apiClient } from '@/lib/api'

// Mock the toast library
jest.mock('sonner', () => ({
  toast: {
    error: jest.fn(),
    success: jest.fn(),
  },
}))

// Mock the apiClient
const mockApiLogin = apiClient.login as jest.MockedFunction<typeof apiClient.login>

describe('LoginForm', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders email and password fields', () => {
    render(<LoginForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    render(<LoginForm />)

    const signInButton = screen.getByRole('button', { name: /sign in/i })
    await user.click(signInButton)

    // Check for error messages (these appear when fields are invalid)
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for invalid email', async () => {
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    await user.type(emailInput, 'invalid-email')
    await user.tab() // Trigger blur event

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for short password', async () => {
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, '123')
    await user.tab() // Trigger blur event

    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('calls apiClient.login with valid credentials', async () => {
    const mockResponse = { access_token: 'test-token' }
    mockApiLogin.mockResolvedValue(mockResponse)

    // Mock the window.location.href assignment
    const mockLocationAssign = jest.fn()
    Object.defineProperty(window, 'location', {
      value: { href: '', assign: mockLocationAssign },
      writable: true,
    })

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const signInButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(signInButton)

    // Verify loading state
    expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument()
    expect(signInButton).toBeDisabled()

    await waitFor(() => {
      expect(mockApiLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      })
    })

    await waitFor(() => {
      expect(mockLocationAssign).toHaveBeenCalledWith('/dashboard')
    })
  })

  it('shows error message on login failure', async () => {
    const errorMessage = 'Invalid credentials'
    mockApiLogin.mockRejectedValue(new Error(errorMessage))

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const signInButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'wrongpassword')
    await user.click(signInButton)

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Login failed')
    })
  })

  it('maintains loading state during API call', async () => {
    mockApiLogin.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const signInButton = screen.getByRole('button', { name: /sign in/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(signInButton)

    // Should show loading state immediately
    expect(screen.getByRole('button', { name: /signing in/i })).toBeInTheDocument()
    expect(signInButton).toBeDisabled()
  })
})