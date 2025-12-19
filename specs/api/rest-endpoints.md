# REST API Endpoints

## Base URL
- Development: http://localhost:8000
- Production: https://api.example.com

## Authentication
All endpoints require JWT token in header:
Authorization: Bearer <token>

## Endpoints

### GET /api/tasks
List all tasks for authenticated user.

Query Parameters:
- search: string (optional) - Search in title and description
- status: "all" | "active" | "completed" (default: "active")
- priority: "low" | "medium" | "high" (optional)
- sort_by: "created_at" | "due_date" | "priority" | "title" (default: "created_at")
- sort_order: "asc" | "desc" (default: "desc")
- limit: number (optional, default: 50)
- offset: number (optional, default: 0)

Response: Array of Task objects

### POST /api/tasks
Create a new task.

Request Body:
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)",
  "priority": "low" | "medium" | "high" (optional, default: "medium"),
  "due_date": "string (optional, ISO 8601 format)"
}
```

Response: Created Task object

### GET /api/tasks/{id}
Get a specific task by ID.

Response: Task object

### PUT /api/tasks/{id}
Update a task.

Request Body: Same as POST, all fields optional

Response: Updated Task object

### PATCH /api/tasks/{id}/complete
Toggle task completion status.

Response: Updated Task object

### DELETE /api/tasks/{id}
Delete a task.

Response: 204 No Content

### GET /api/users/me
Get current user information.

Response: User object

### GET /api/users/me/export
Export user data as JSON file.

Response: JSON file download

### PUT /api/users/me/preferences
Update user preferences.

Request Body:
```json
{
  "preferences": {
    "showCompleted": boolean,
    "compactView": boolean,
    "darkMode": boolean
  }
}
```

Response: 200 OK

### Authentication Endpoints
- POST /api/auth/register - Register new user
- POST /api/auth/login - Login user
- POST /api/auth/logout - Logout user