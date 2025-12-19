# Feature: Task CRUD Operations

## User Stories
- As a user, I can create a new task
- As a user, I can view all my tasks
- As a user, I can update a task
- As a user, I can delete a task
- As a user, I can mark a task complete

## Acceptance Criteria

### Create Task
- Title is required (1-200 characters)
- Description is optional (max 1000 characters)
- Priority can be LOW, MEDIUM, or HIGH (default: MEDIUM)
- Task is associated with logged-in user
- Due date is optional

### View Tasks
- Only show tasks for current user
- Display title, description, priority, status, created date
- Support filtering by status (all, active, completed)
- Support sorting by created date, due date, priority
- Support search by title and description

### Update Task
- User can edit title, description, priority, due date
- User can toggle completion status
- Updates are reflected immediately in UI

### Delete Task
- Confirmation dialog before deletion
- Task is permanently removed from database
- UI updates to reflect deletion