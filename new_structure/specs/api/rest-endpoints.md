# REST API Endpoints Specification

## Overview
This specification defines the complete REST API for the Todo Evolution application across all phases (I-III). The API follows RESTful principles and uses OpenAPI 3.0 for documentation.

## Base Configuration
- **Base URL**: `https://api.todoapp.com/v1`
- **Content-Type**: `application/json`
- **Authentication**: Bearer Token (JWT)
- **Rate Limiting**: 100 requests per minute per user

## Standard Response Format

### Success Response
```json
{
  "success": true,
  "data": {}, // Response data
  "message": "Operation completed successfully",
  "timestamp": "2025-12-21T10:30:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "title",
        "message": "Title is required"
      }
    ]
  },
  "timestamp": "2025-12-21T10:30:00Z"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": {
    "items": [], // Array of items
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "Data retrieved successfully",
  "timestamp": "2025-12-21T10:30:00Z"
}
```

## Authentication Endpoints

### Register User
```
POST /api/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_verified": false,
      "created_at": "2025-12-21T10:30:00Z"
    }
  },
  "message": "User registered successfully. Please check your email to verify your account."
}
```

### Login
```
POST /api/auth/login
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "remember_me": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_verified": true
    }
  },
  "message": "Login successful"
}
```

### Refresh Token
```
POST /api/auth/refresh
```

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  },
  "message": "Token refreshed successfully"
}
```

### Logout
```
POST /api/auth/logout
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### Forgot Password
```
POST /api/auth/forgot-password
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Password reset email sent"
}
```

### Reset Password
```
POST /api/auth/reset-password
```

**Request Body**:
```json
{
  "token": "reset_token_here",
  "password": "NewSecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Password reset successfully"
}
```

## User Endpoints

### Get Current User
```
GET /api/users/me
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_verified": true,
    "created_at": "2025-12-21T10:30:00Z",
    "last_login": "2025-12-21T09:15:00Z"
  }
}
```

### Update Current User
```
PUT /api/users/me
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "full_name": "John Smith",
  "email": "johnsmith@example.com"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "johnsmith@example.com",
    "full_name": "John Smith",
    "is_verified": true,
    "updated_at": "2025-12-21T10:45:00Z"
  },
  "message": "User updated successfully"
}
```

### Change Password
```
PUT /api/users/me/password
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "current_password": "CurrentPass123!",
  "new_password": "NewSecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

## Task Endpoints

### List Tasks
```
GET /api/tasks
```

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `status`: Filter by status (`pending`, `completed`, `all`)
- `priority`: Filter by priority (`low`, `medium`, `high`, `urgent`)
- `category`: Filter by category
- `due_date`: Filter by due date (`today`, `week`, `overdue`)
- `search`: Search in title and description
- `sort`: Sort field (`created_at`, `updated_at`, `due_date`, `priority`)
- `order`: Sort order (`asc`, `desc`)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the API endpoints",
        "status": "pending",
        "priority": "high",
        "category": "work",
        "due_date": "2025-12-25T23:59:59Z",
        "created_at": "2025-12-21T10:30:00Z",
        "updated_at": "2025-12-21T10:30:00Z",
        "completed_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "message": "Tasks retrieved successfully"
}
```

### Create Task
```
POST /api/tasks
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the API endpoints",
  "priority": "high",
  "category": "work",
  "due_date": "2025-12-25T23:59:59Z"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the API endpoints",
    "status": "pending",
    "priority": "high",
    "category": "work",
    "due_date": "2025-12-25T23:59:59Z",
    "created_at": "2025-12-21T10:30:00Z",
    "updated_at": "2025-12-21T10:30:00Z",
    "completed_at": null
  },
  "message": "Task created successfully"
}
```

### Get Task
```
GET /api/tasks/{task_id}
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the API endpoints",
    "status": "pending",
    "priority": "high",
    "category": "work",
    "due_date": "2025-12-25T23:59:59Z",
    "created_at": "2025-12-21T10:30:00Z",
    "updated_at": "2025-12-21T10:30:00Z",
    "completed_at": null
  }
}
```

### Update Task
```
PUT /api/tasks/{task_id}
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "Complete API documentation",
  "description": "Write comprehensive documentation for all API endpoints",
  "status": "completed",
  "priority": "urgent",
  "category": "work",
  "due_date": "2025-12-24T23:59:59Z"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Complete API documentation",
    "description": "Write comprehensive documentation for all API endpoints",
    "status": "completed",
    "priority": "urgent",
    "category": "work",
    "due_date": "2025-12-24T23:59:59Z",
    "created_at": "2025-12-21T10:30:00Z",
    "updated_at": "2025-12-21T11:00:00Z",
    "completed_at": "2025-12-21T11:00:00Z"
  },
  "message": "Task updated successfully"
}
```

### Delete Task
```
DELETE /api/tasks/{task_id}
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

### Update Task Status
```
PATCH /api/tasks/{task_id}/status
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "status": "completed"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "completed",
    "completed_at": "2025-12-21T11:00:00Z"
  },
  "message": "Task status updated successfully"
}
```

### Search Tasks
```
GET /api/tasks/search
```

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `q`: Search query (required)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the API endpoints",
        "status": "pending",
        "priority": "high",
        "created_at": "2025-12-21T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    },
    "search_info": {
      "query": "documentation",
      "total_results": 1
    }
  },
  "message": "Search completed successfully"
}
```

## Bulk Operations

### Bulk Update Tasks
```
PATCH /api/tasks/bulk
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "task_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "updates": {
    "status": "completed",
    "category": "work"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "updated_count": 2,
    "failed_count": 0,
    "errors": []
  },
  "message": "Bulk update completed successfully"
}
```

### Bulk Delete Tasks
```
DELETE /api/tasks/bulk
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "task_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "deleted_count": 2
  },
  "message": "Tasks deleted successfully"
}
```

## Statistics Endpoints

### Get Task Statistics
```
GET /api/tasks/stats
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "total_tasks": 25,
    "pending_tasks": 15,
    "completed_tasks": 10,
    "overdue_tasks": 3,
    "tasks_due_today": 2,
    "tasks_due_this_week": 8,
    "completion_rate": 0.4,
    "tasks_by_priority": {
      "low": 5,
      "medium": 12,
      "high": 6,
      "urgent": 2
    },
    "tasks_by_category": {
      "work": 15,
      "personal": 8,
      "shopping": 2
    }
  },
  "message": "Statistics retrieved successfully"
}
```

## Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid input data |
| UNAUTHORIZED | 401 | No authentication provided |
| FORBIDDEN | 403 | User not authorized for resource |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict (e.g., duplicate email) |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Internal server error |
| SERVICE_UNAVAILABLE | 503 | Service temporarily unavailable |

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute per IP
- **General endpoints**: 100 requests per minute per user
- **Search endpoints**: 20 requests per minute per user
- **Bulk operations**: 10 requests per minute per user

## Versioning

- Current version: `v1`
- Version specified in URL: `/api/v1/...`
- Backward compatibility maintained for at least 2 versions
- Depreciation warnings in response headers for old versions

## Phase III: Chat API Endpoints

### Conversation Management

#### Create New Conversation
```
POST /api/conversations
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "title": "Project planning session"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "conversation": {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Project planning session",
      "created_at": "2025-12-21T10:30:00Z",
      "updated_at": "2025-12-21T10:30:00Z"
    }
  },
  "message": "Conversation created successfully"
}
```

#### Get User Conversations
```
GET /api/conversations
```

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "title": "Project planning session",
        "created_at": "2025-12-21T10:30:00Z",
        "updated_at": "2025-12-21T11:00:00Z",
        "message_count": 15,
        "last_message": "Let's review the project timeline"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "message": "Conversations retrieved successfully"
}
```

#### Get Conversation with Messages
```
GET /api/conversations/{conversation_id}
```

**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Messages per page (default: 50)

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "conversation": {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Project planning session",
      "created_at": "2025-12-21T10:30:00Z",
      "messages": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440004",
          "role": "user",
          "content": "Create a task for the project kickoff",
          "timestamp": "2025-12-21T10:30:00Z"
        },
        {
          "id": "550e8400-e29b-41d4-a716-446655440005",
          "role": "assistant",
          "content": "I've created a task 'Project kickoff meeting' for tomorrow at 10 AM. Would you like me to add any specific agenda items?",
          "timestamp": "2025-12-21T10:30:15Z",
          "tool_calls": [
            {
              "tool": "create_task",
              "parameters": {
                "title": "Project kickoff meeting",
                "due_date": "2025-12-22T10:00:00Z"
              }
            }
          ]
        }
      ]
    },
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 2,
      "pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

#### Delete Conversation
```
DELETE /api/conversations/{conversation_id}
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Conversation deleted successfully"
}
```

### Chat Message Processing

#### Send Message to AI Assistant
```
POST /api/conversations/{conversation_id}/messages
```

**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "message": "Create a task for the project kickoff meeting",
  "context": {
    "current_view": "dashboard",
    "selected_task_id": "550e8400-e29b-41d4-a716-446655440001"
  },
  "stream": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "550e8400-e29b-41d4-a716-446655440006",
      "role": "assistant",
      "content": "I've created a task 'Project kickoff meeting' for tomorrow at 10 AM. Would you like me to add any specific agenda items?",
      "timestamp": "2025-12-21T10:30:15Z",
      "tool_calls": [
        {
          "tool": "create_task",
          "parameters": {
            "title": "Project kickoff meeting",
            "due_date": "2025-12-22T10:00:00Z"
          },
          "result": {
            "task_id": "550e8400-e29b-41d4-a716-446655440007",
            "status": "created"
          }
        }
      ]
    },
    "suggested_followups": [
      "Add agenda items to the task",
      "Invite team members",
      "Book meeting room"
    ]
  },
  "message": "Message processed successfully"
}
```

#### Stream Chat Response (Server-Sent Events)
```
GET /api/conversations/{conversation_id}/messages
```

**Headers**:
- `Authorization: Bearer {access_token}`
- `Accept: text/event-stream`

**Query Parameters**:
- `message`: The message to send
- `context`: Optional context JSON

**Response** (Server-Sent Events):
```
data: {"type": "start", "message_id": "uuid"}

data: {"type": "token", "content": "I'm"}

data: {"type": "token", "content": " creating"}

data: {"type": "token", "content": " a"}

data: {"type": "tool_call", "tool": "create_task", "parameters": {...}}

data: {"type": "tool_result", "tool": "create_task", "result": {"task_id": "uuid"}}

data: {"type": "token", "content": " Task created!"}

data: {"type": "end", "message": {"id": "uuid", "content": "I've created the task successfully"}}
```

### AI Context Management

#### Load Conversation Context
```
GET /api/conversations/{conversation_id}/context
```

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "context": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "total_tasks": 45,
      "pending_tasks": 25,
      "recent_tasks": [
        {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "title": "Review documentation",
          "status": "pending",
          "priority": "high"
        }
      ],
      "categories": ["work", "personal", "project"],
      "conversation_history": [
        {
          "role": "user",
          "content": "Create a task for documentation",
          "timestamp": "2025-12-21T10:00:00Z"
        }
      ],
      "current_time": "2025-12-21T10:30:00Z",
      "user_preferences": {
        "default_priority": "medium",
        "timezone": "UTC",
        "working_hours": "09:00-17:00"
      }
    }
  },
  "message": "Context loaded successfully"
}
```

## WebSocket Events (Future Enhancement)

```typescript
// WebSocket connection URL
wss://api.todoapp.com/v1/ws

// Events
interface TaskEvent {
  type: 'task_created' | 'task_updated' | 'task_deleted';
  task: Task;
  timestamp: string;
}

interface AuthEvent {
  type: 'token_expired' | 'session_invalidated';
  message: string;
  timestamp: string;
}
```

## OpenAPI Documentation

The API is fully documented using OpenAPI 3.0 specification. Interactive documentation available at:
- **Swagger UI**: `/api/docs`
- **ReDoc**: `/api/redoc`
- **OpenAPI JSON**: `/api/openapi.json`