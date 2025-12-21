# Phase II: Authentication & Authorization Specification

## Overview
Phase II implements a comprehensive authentication and authorization system using Better Auth with JWT tokens. This system ensures secure user management, proper session handling, and protects all API endpoints with robust security measures.

## Authentication Flow

### 1. User Registration
- Email-based registration with verification
- Strong password requirements
- Optional display name
- Automatic user profile creation

### 2. User Login
- JWT-based authentication
- Secure password verification
- Remember me functionality
- Automatic token refresh

### 3. Session Management
- Short-lived access tokens (15 minutes)
- Long-lived refresh tokens (7 days)
- Secure token storage
- Logout with token invalidation

## User Stories

### Story 1: User Registration
**As a** new user
**I want to** create an account with email and password
**So that** I can have my own private todo list

**Acceptance Criteria**:
- Unique user ID field (3-50 chars, alphanumeric + underscore/hyphen)
- Email validation with format checking
- Password strength requirements (8+ chars, uppercase, lowercase, number, special)
- Password hashed with bcrypt
- Optional display name field
- Email verification required before access

### Story 2: User Login
**As a** registered user
**I want to** log in securely with my credentials
**So that** I can access my private todo list

**Acceptance Criteria**:
- Email and password login form
- "Remember me" option (7-day session vs 15-minute)
- Rate limiting (5 attempts per 15 minutes)
- JWT tokens returned on success
- Clear error messages for invalid credentials

### Story 3: Session Management
**As a** logged-in user
**I want to** maintain my session securely
**So that** I don't have to log in repeatedly

**Acceptance Criteria**:
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Automatic token refresh in background
- Secure storage in localStorage
- All tokens invalidated on logout

### Story 4: Password Recovery
**As a** user who forgot their password
**I want to** reset my password via email
**So that** I can regain access to my account

**Acceptance Criteria**:
- Password reset request with email
- Secure reset token (expires in 1 hour)
- Email with reset link
- Password reset form
- All sessions invalidated after reset

### Story 5: Protected Access
**As a** logged-in user
**I want to** access only my own data
**So that** my privacy is protected

**Acceptance Criteria**:
- All API endpoints require valid JWT
- Users can only access their own tasks
- Token validation on every request
- 401 response for invalid/expired tokens
- Automatic redirect to login on token expiry

## Implementation Details

### Backend Setup (Better Auth)

#### Configuration
```python
# backend/app/core/auth.py
from better_auth import Auth
from better_auth.adapters.fastapi import FastAPIAuth
from app.core.config import settings
from app.models.user import User

# Initialize Better Auth
auth = Auth(
    database_url=settings.DATABASE_URL,
    secret_key=settings.SECRET_KEY,
    social_providers={
        "google": {
            "clientId": settings.GOOGLE_CLIENT_ID,
            "clientSecret": settings.GOOGLE_CLIENT_SECRET,
        },
        "github": {
            "clientId": settings.GITHUB_CLIENT_ID,
            "clientSecret": settings.GITHUB_CLIENT_SECRET,
        },
    },
    emailAndPassword={
        "enabled": True,
        "requireEmailVerification": True,
    },
    session={
        "expiresIn": 60 * 15,  # 15 minutes for access token
        "refreshTokenExpiresIn": 60 * 60 * 24 * 7,  # 7 days for refresh
    },
    callbacks={
        "afterSignIn": async (user) => {
            # Post-signin logic (logging, analytics)
            pass
        },
        "beforeSignUp": async (data) => {
            # Pre-signup validation
            if not data.get("email"):
                raise ValueError("Email is required")
            return data
        },
    }
)

# FastAPI integration
fastapi_auth = FastAPIAuth(auth)
```

#### User Model
```python
# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from uuid import uuid4
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    image_url = Column(String(500), nullable=True)
    metadata = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user")
    messages = relationship("Message", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

#### API Routes
```python
# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import fastapi_auth
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)
import jwt

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.user_id == request.user_id)
        ).first()

        if existing_user:
            if existing_user.email == request.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User ID already taken"
                )

        # Create user with Better Auth
        user = await fastapi_auth.auth.api.sign_up_email_password(
            email=request.email,
            password=request.password,
            name=request.name,
            user_id=request.user_id,
            callback_url=None  # Will use default email verification
        )

        # Store additional user data in our database
        db_user = User(
            user_id=request.user_id,
            email=request.email,
            name=request.name,
            password_hash=user.passwordHash,  # Already hashed by Better Auth
            email_verified=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Generate tokens
        tokens = await fastapi_auth.auth.api.sign_in_email_password(
            email=request.email,
            password=request.password
        )

        return AuthResponse(
            user=UserResponse.from_orm(db_user),
            access_token=tokens.token,
            refresh_token=tokens.refreshToken,
            expires_in=900  # 15 minutes
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Sign in user with email and password."""
    try:
        # Authenticate with Better Auth
        tokens = await fastapi_auth.auth.api.sign_in_email_password(
            email=request.email,
            password=request.password,
            remember_me=request.remember_me
        )

        # Get user from our database
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        return AuthResponse(
            user=UserResponse.from_orm(user),
            access_token=tokens.token,
            refresh_token=tokens.refreshToken,
            expires_in=900 if not request.remember_me else 604800  # 15 min or 7 days
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    try:
        tokens = await fastapi_auth.auth.api.refresh_session(refresh_token)

        # Get user from token
        payload = jwt.decode(tokens.token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return AuthResponse(
            user=UserResponse.from_orm(user),
            access_token=tokens.token,
            refresh_token=tokens.refreshToken,
            expires_in=900
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout user and invalidate tokens."""
    try:
        # Better Auth handles session invalidation
        await fastapi_auth.auth.api.sign_out(credentials.credentials)
        return {"message": "Logged out successfully"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Send password reset email."""
    try:
        await fastapi_auth.auth.api.forget_password(request.email)
        return {"message": "Password reset email sent"}
    except Exception:
        # Always return success to prevent email enumeration
        return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    """Reset password with token."""
    try:
        await fastapi_auth.auth.api.reset_password(
            token=request.token,
            password=request.password
        )
        return {"message": "Password reset successful"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    try:
        # Verify token with Better Auth
        session = await fastapi_auth.auth.api.getSession(credentials.credentials)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get user from our database
        user = db.query(User).filter(User.user_id == session.user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.from_orm(user)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

#### Authentication Dependencies
```python
# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import fastapi_auth
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    try:
        # Verify session with Better Auth
        session = await fastapi_auth.auth.api.getSession(credentials.credentials)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        # Get user from database
        user = db.query(User).filter(User.user_id == session.user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified"
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user
```

### Frontend Implementation

#### Auth Context
```typescript
// frontend/src/contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { User } from '@/types'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
}

interface AuthContextType extends AuthState {
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  forgotPassword: (email: string) => Promise<void>
  resetPassword: (token: string, password: string) => Promise<void>
}

interface RegisterData {
  userId: string
  email: string
  password: string
  name?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false
  })

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')

      if (token && refreshToken) {
        try {
          // Verify token and get user
          const user = await getCurrentUser()
          setState({
            user,
            isLoading: false,
            isAuthenticated: true
          })
        } catch (error) {
          // Token invalid, try refresh
          try {
            await refreshAccessToken()
            const user = await getCurrentUser()
            setState({
              user,
              isLoading: false,
              isAuthenticated: true
            })
          } catch (refreshError) {
            // Both tokens invalid, clear storage
            clearTokens()
            setState({
              user: null,
              isLoading: false,
              isAuthenticated: false
            })
          }
        }
      } else {
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false
        })
      }
    }

    initAuth()
  }, [])

  const login = async (email: string, password: string, rememberMe = false) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, rememberMe })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()

    // Store tokens
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)

    setState({
      user: data.user,
      isLoading: false,
      isAuthenticated: true
    })
  }

  const register = async (userData: RegisterData) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    const data = await response.json()

    // Store tokens
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)

    setState({
      user: data.user,
      isLoading: false,
      isAuthenticated: true
    })
  }

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearTokens()
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false
      })
    }
  }

  const refreshToken = async () => {
    const refresh_token = localStorage.getItem('refresh_token')
    if (!refresh_token) {
      throw new Error('No refresh token')
    }

    const response = await fetch('/api/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token })
    })

    if (!response.ok) {
      clearTokens()
      throw new Error('Token refresh failed')
    }

    const data = await response.json()

    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)

    setState(prev => ({
      ...prev,
      user: data.user
    }))
  }

  const clearTokens = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return (
    <AuthContext.Provider value={{
      ...state,
      login,
      register,
      logout,
      refreshToken,
      forgotPassword: async (email: string) => {
        await fetch('/api/auth/forgot-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        })
      },
      resetPassword: async (token: string, password: string) => {
        await fetch('/api/auth/reset-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token, password })
        })
      }
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Helper function to get current user
async function getCurrentUser(): Promise<User> {
  const token = localStorage.getItem('access_token')
  if (!token) {
    throw new Error('No access token')
  }

  const response = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })

  if (!response.ok) {
    throw new Error('Failed to get user')
  }

  return response.json()
}

// Helper function to refresh access token
async function refreshAccessToken(): Promise<void> {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    throw new Error('No refresh token')
  }

  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  })

  if (!response.ok) {
    throw new Error('Failed to refresh token')
  }

  const data = await response.json()
  localStorage.setItem('access_token', data.access_token)
  localStorage.setItem('refresh_token', data.refresh_token)
}
```

#### Login Component
```typescript
// frontend/src/components/auth/LoginForm.tsx
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Link, useNavigate, useLocation } from 'react-router-dom'

export function LoginForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = location.state?.from?.pathname || '/dashboard'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(formData.email, formData.password, formData.rememberMe)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email
          </label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            placeholder="Enter your email"
            required
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password
          </label>
          <Input
            id="password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
            placeholder="Enter your password"
            required
            disabled={isLoading}
          />
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="rememberMe"
            checked={formData.rememberMe}
            onCheckedChange={(checked) =>
              setFormData(prev => ({ ...prev, rememberMe: !!checked }))
            }
            disabled={isLoading}
          />
          <label htmlFor="rememberMe" className="text-sm">
            Remember me for 7 days
          </label>
        </div>

        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign in'}
        </Button>

        <div className="text-center text-sm">
          <Link to="/forgot-password" className="text-blue-600 hover:underline">
            Forgot your password?
          </Link>
        </div>
      </form>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-gray-500">Or continue with</span>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3">
          <Button variant="outline" disabled={isLoading}>
            <img src="/google-icon.svg" alt="Google" className="w-5 h-5 mr-2" />
            Google
          </Button>
          <Button variant="outline" disabled={isLoading}>
            <img src="/github-icon.svg" alt="GitHub" className="w-5 h-5 mr-2" />
            GitHub
          </Button>
        </div>
      </div>

      <p className="mt-8 text-center text-sm text-gray-600">
        Don't have an account?{' '}
        <Link to="/register" className="font-medium text-blue-600 hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  )
}
```

#### Register Component
```typescript
// frontend/src/components/auth/RegisterForm.tsx
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Link, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle } from 'lucide-react'

export function RegisterForm() {
  const [formData, setFormData] = useState({
    userId: '',
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [passwordValidation, setPasswordValidation] = useState({
    minLength: false,
    hasUpper: false,
    hasLower: false,
    hasNumber: false,
    hasSpecial: false
  })

  const { register } = useAuth()
  const navigate = useNavigate()

  const validatePassword = (password: string) => {
    setPasswordValidation({
      minLength: password.length >= 8,
      hasUpper: /[A-Z]/.test(password),
      hasLower: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    })
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const password = e.target.value
    setFormData(prev => ({ ...prev, password }))
    validatePassword(password)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!Object.values(passwordValidation).every(Boolean)) {
      setError('Password does not meet requirements')
      return
    }

    setIsLoading(true)

    try {
      await register({
        userId: formData.userId,
        email: formData.email,
        password: formData.password,
        name: formData.name || undefined
      })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const isPasswordValid = Object.values(passwordValidation).every(Boolean)

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div>
          <label htmlFor="userId" className="block text-sm font-medium mb-1">
            User ID *
          </label>
          <Input
            id="userId"
            type="text"
            value={formData.userId}
            onChange={(e) => setFormData(prev => ({ ...prev, userId: e.target.value }))}
            placeholder="Choose a unique user ID"
            required
            disabled={isLoading}
            minLength={3}
            maxLength={50}
            pattern="[a-zA-Z0-9_-]+"
            title="Only letters, numbers, underscore, and hyphen allowed"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">
            Email *
          </label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
            placeholder="Enter your email"
            required
            disabled={isLoading}
          />
        </div>

        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">
            Display Name
          </label>
          <Input
            id="name"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="Enter your name (optional)"
            disabled={isLoading}
            maxLength={100}
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium mb-1">
            Password *
          </label>
          <Input
            id="password"
            type="password"
            value={formData.password}
            onChange={handlePasswordChange}
            placeholder="Create a password"
            required
            disabled={isLoading}
            minLength={8}
          />

          {formData.password && (
            <div className="mt-2 space-y-1">
              <div className="flex items-center text-xs">
                {passwordValidation.minLength ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-500 mr-1" />
                )}
                At least 8 characters
              </div>
              <div className="flex items-center text-xs">
                {passwordValidation.hasUpper ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-500 mr-1" />
                )}
                One uppercase letter
              </div>
              <div className="flex items-center text-xs">
                {passwordValidation.hasLower ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-500 mr-1" />
                )}
                One lowercase letter
              </div>
              <div className="flex items-center text-xs">
                {passwordValidation.hasNumber ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-500 mr-1" />
                )}
                One number
              </div>
              <div className="flex items-center text-xs">
                {passwordValidation.hasSpecial ? (
                  <CheckCircle className="w-3 h-3 text-green-500 mr-1" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-500 mr-1" />
                )}
                One special character
              </div>
            </div>
          )}
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1">
            Confirm Password *
          </label>
          <Input
            id="confirmPassword"
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
            placeholder="Confirm your password"
            required
            disabled={isLoading}
          />
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={isLoading || !isPasswordValid || !formData.confirmPassword}
        >
          {isLoading ? 'Creating account...' : 'Create account'}
        </Button>
      </form>

      <p className="mt-8 text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link to="/login" className="font-medium text-blue-600 hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  )
}
```

#### Protected Route Component
```typescript
// frontend/src/components/auth/ProtectedRoute.tsx
import { useAuth } from '@/contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
```

### API Client with Auth
```typescript
// frontend/src/lib/api.ts
import { useAuth } from '@/contexts/AuthContext'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private getAuthHeaders() {
    const token = localStorage.getItem('access_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    }

    let response = await fetch(url, config)

    // Handle token refresh
    if (response.status === 401) {
      try {
        // Try to refresh the token
        const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            refresh_token: localStorage.getItem('refresh_token')
          })
        })

        if (refreshResponse.ok) {
          const data = await refreshResponse.json()
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)

          // Retry the original request
          config.headers = {
            ...config.headers,
            Authorization: `Bearer ${data.access_token}`
          }
          response = await fetch(url, config)
        } else {
          // Refresh failed, redirect to login
          window.location.href = '/login'
          throw new Error('Session expired')
        }
      } catch (error) {
        window.location.href = '/login'
        throw new Error('Session expired')
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }))
      throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(email: string, password: string, rememberMe = false) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, rememberMe })
    })
  }

  async register(userData: any) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST'
    })
  }

  // Task endpoints
  async getTasks(params?: any) {
    const query = new URLSearchParams(params).toString()
    return this.request(`/tasks?${query}`)
  }

  async createTask(taskData: any) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData)
    })
  }

  async updateTask(id: string, taskData: any) {
    return this.request(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData)
    })
  }

  async deleteTask(id: string) {
    return this.request(`/tasks/${id}`, {
      method: 'DELETE'
    })
  }
}

export const apiClient = new ApiClient()
```

## Security Measures

### 1. Password Security
- Minimum 8 characters
- Complexity requirements (uppercase, lowercase, numbers, special characters)
- Hashed with bcrypt (handled by Better Auth)
- Password reset tokens expire after 1 hour

### 2. Token Security
- JWT access tokens with 15-minute expiry
- Secure refresh tokens with 7-day expiry
- Tokens stored in httpOnly cookies or secure localStorage
- Automatic token refresh mechanism
- Token invalidation on logout

### 3. API Security
- All endpoints protected by default
- Rate limiting on auth endpoints
- CORS properly configured
- SQL injection prevention through ORM
- XSS prevention in frontend

### 4. Email Verification
- Required before accessing protected resources
- Verification links expire after 24 hours
- Resend verification option

## Environment Variables

### Backend (.env)
```env
# Better Auth Configuration
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-better-auth-secret

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Backend Tests
```python
# backend/tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models.user import User

client = TestClient(app)

def test_register_success():
    response = client.post("/auth/register", json={
        "userId": "testuser123",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "name": "Test User"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_register_duplicate_email():
    # First registration
    client.post("/auth/register", json={
        "userId": "user1",
        "email": "duplicate@example.com",
        "password": "SecurePass123!"
    })

    # Second registration with same email
    response = client.post("/auth/register", json={
        "userId": "user2",
        "email": "duplicate@example.com",
        "password": "SecurePass123!"
    })

    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success():
    # Register user first
    client.post("/auth/register", json={
        "userId": "loginuser",
        "email": "login@example.com",
        "password": "SecurePass123!"
    })

    # Login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "SecurePass123!"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_invalid_credentials():
    response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpass"
    })

    assert response.status_code == 401

def test_protected_endpoint_without_token():
    response = client.get("/auth/me")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    # Register and login
    register_response = client.post("/auth/register", json={
        "userId": "protecteduser",
        "email": "protected@example.com",
        "password": "SecurePass123!"
    })

    token = register_response.json()["access_token"]

    # Access protected endpoint
    response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    assert response.json()["email"] == "protected@example.com"
```

### Frontend Tests
```typescript
// frontend/src/components/auth/__tests__/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { LoginForm } from '../LoginForm'
import { AuthProvider } from '@/contexts/AuthContext'

// Mock the auth context
const mockLogin = jest.fn()

jest.mock('@/contexts/AuthContext', () => ({
  ...jest.requireActual('@/contexts/AuthContext'),
  useAuth: () => ({
    login: mockLogin
  })
}))

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  )
}

describe('LoginForm', () => {
  beforeEach(() => {
    mockLogin.mockClear()
  })

  it('renders login form correctly', () => {
    renderWithProviders(<LoginForm />)

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    renderWithProviders(<LoginForm />)

    const submitButton = screen.getByRole('button', { name: /sign in/i })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByLabelText(/email/i)).toBeInvalid()
      expect(screen.getByLabelText(/^password/i)).toBeInvalid()
    })
  })

  it('calls login with correct credentials', async () => {
    mockLogin.mockResolvedValue(undefined)

    renderWithProviders(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123', false)
    })
  })

  it('shows error message on login failure', async () => {
    mockLogin.mockRejectedValue(new Error('Invalid credentials'))

    renderWithProviders(<LoginForm />)

    const emailInput = screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/^password/i)
    const submitButton = screen.getByRole('button', { name: /sign in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument()
    })
  })
})
```

## Success Metrics

### Security Metrics
- 0 successful brute force attacks
- 0 unauthorized API accesses
- 100% of passwords hashed and salted
- All tokens expire properly
- Email verification rate > 90%

### User Experience Metrics
- Login success rate > 95%
- Registration completion rate > 80%
- Password reset success rate > 90%
- Average login time < 2 seconds
- Token refresh success rate > 99%

### Technical Metrics
- API response time for auth endpoints < 500ms
- Zero authentication-related errors in production
- All auth endpoints properly rate limited
- Secure configuration for all environments

This comprehensive authentication and authorization system ensures secure user management while providing a smooth user experience across the Todo Evolution application.