# Database Schema

## Tables

### users
- id: INTEGER (primary key, auto-increment)
- email: VARCHAR (unique, not null)
- hashed_password: VARCHAR (not null)
- preferences: JSONB (nullable, stores user preferences)
- created_at: TIMESTAMP (default: NOW())
- updated_at: TIMESTAMP (default: NOW(), updated on change)

### tasks
- id: INTEGER (primary key, auto-increment)
- user_id: INTEGER (foreign key -> users.id, not null)
- title: VARCHAR(200) (not null)
- description: TEXT (nullable)
- priority: VARCHAR(10) (not null, default: 'MEDIUM', check: priority IN ('LOW', 'MEDIUM', 'HIGH'))
- due_date: TIMESTAMP (nullable)
- completed: BOOLEAN (default: false)
- created_at: TIMESTAMP (default: NOW())
- updated_at: TIMESTAMP (default: NOW(), updated on change)

## Indexes
- users.email (unique index)
- tasks.user_id (for filtering by user)
- tasks.completed (for status filtering)
- tasks.priority (for priority filtering)
- tasks.due_date (for date-based queries)
- Composite index: (user_id, completed, created_at)

## Constraints
- Tasks must have a valid user_id (foreign key constraint)
- Email must be unique across all users
- Task title cannot be empty
- Task priority must be one of: LOW, MEDIUM, HIGH