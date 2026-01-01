# API Documentation Example

Complete API documentation with OpenAPI/Swagger spec.

## Base URL

- **Development**: http://localhost:8000
- **Production**: https://api.example.com

## Authentication

All authenticated endpoints require a JWT token:

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Register User
**POST** `/auth/register`

Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "johndoe"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Errors**:
- `400`: Validation error (email exists, weak password)
- `422`: Invalid input format

---

#### Login
**POST** `/auth/login`

Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response 200**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors**:
- `401`: Invalid credentials

---

### Tasks

#### List Tasks
**GET** `/tasks/`

Get paginated list of tasks for authenticated user.

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max: 100) |
| `status` | string | - | Filter by status (pending, in_progress, completed) |
| `search` | string | - | Search in title and description |

**Request**:
```
GET /tasks/?page=1&page_size=20&status=pending
Authorization: Bearer <token>
```

**Response 200**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Complete project",
      "description": "Finish the CRUD implementation",
      "status": "pending",
      "priority": "high",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

#### Create Task
**POST** `/tasks/`

Create a new task.

**Request Body**:
```json
{
  "title": "New task",
  "description": "Task description",
  "priority": "high",
  "due_date": "2025-01-20T00:00:00Z"
}
```

**Response 201**:
```json
{
  "id": 43,
  "title": "New task",
  "description": "Task description",
  "status": "pending",
  "priority": "high",
  "due_date": "2025-01-20T00:00:00Z",
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

**Errors**:
- `400`: Validation error
- `401`: Unauthorized

---

#### Get Task
**GET** `/tasks/{task_id}`

Get a specific task by ID.

**Response 200**:
```json
{
  "id": 1,
  "title": "Task title",
  "description": "Task description",
  "status": "pending",
  "priority": "normal",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

**Errors**:
- `401`: Unauthorized
- `404`: Task not found

---

#### Update Task
**PATCH** `/tasks/{task_id}`

Update a task. Only include fields to update.

**Request Body**:
```json
{
  "status": "in_progress",
  "priority": "high"
}
```

**Response 200**:
```json
{
  "id": 1,
  "title": "Task title",
  "status": "in_progress",
  "priority": "high",
  "updated_at": "2025-01-15T11:30:00Z"
}
```

**Errors**:
- `400`: Validation error
- `401`: Unauthorized
- `404`: Task not found

---

#### Delete Task
**DELETE** `/tasks/{task_id}`

Delete a task.

**Response 204**: No Content

**Errors**:
- `401`: Unauthorized
- `404`: Task not found

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Rate Limiting

- **Authenticated**: 1000 requests/hour
- **Unauthenticated**: 100 requests/hour

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642281600
```
