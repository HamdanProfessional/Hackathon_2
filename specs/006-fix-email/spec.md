# Feature Specification: Email Notification System

**Feature Branch**: `006-fix-email`
**Created**: 2025-12-27
**Status**: Implemented
**Input**: Fix email notifications using custom email API bypassing Dapr pub/sub complexity

## User Scenarios & Testing

### User Story 1 - Task Creation Email Notification (Priority: P1)

Users receive immediate email notification when they create a new task, confirming the task was successfully added to their todo list.

**Why this priority**: This is the core notification feature - users need confirmation that tasks are being created successfully. It's the foundation for all other task notifications.

**Independent Test**: Can be fully tested by creating a single task and verifying email arrives at user's registered email address. Delivers immediate value by providing task creation confirmation.

**Acceptance Scenarios**:

1. **Given** a logged-in user with a registered email address, **When** they create a new task via the web interface or API, **Then** they receive an HTML email at their registered address containing the task title, description, and a confirmation message
2. **Given** a user creates a task without a description, **When** the email is sent, **Then** the email displays the task title with "No description" placeholder
3. **Given** the email service is temporarily unavailable, **When** a task is created, **Then** the task is still saved successfully and an error is logged for later investigation (non-blocking)

---

### User Story 2 - Task Completion Email Notification (Priority: P2)

Users receive congratulatory email notification when they mark a task as complete, providing positive reinforcement and closure.

**Why this priority**: While important for user engagement, task completion is a secondary action. Users can still function without completion emails, but it enhances satisfaction and motivation.

**Independent Test**: Can be fully tested by creating a task, marking it complete, and verifying congratulatory email arrives. Delivers value by acknowledging user productivity.

**Acceptance Scenarios**:

1. **Given** an existing incomplete task, **When** the user marks it as complete, **Then** they receive an email with "Task Completed" status badge and congratulatory message
2. **Given** a task already marked as complete, **When** the user toggles it back to incomplete, **Then** no completion email is sent (no notification for un-completing)
3. **Given** a completed task, **When** the completion email is viewed, **Then** it displays task details with a green "COMPLETED" badge and positive reinforcement message

---

### User Story 3 - Task Update and Delete Notifications (Priority: P3)

Users receive email notifications when they update task details or delete a task, keeping them informed of all changes to their todo list.

**Why this priority**: Update and delete notifications are useful but less critical than creation/completion. Users already see immediate feedback in the UI, so emails serve as audit trail rather than primary confirmation.

**Independent Test**: Can be fully tested by updating a task title/description and verifying email arrives, then deleting the task and verifying deletion email. Delivers value by maintaining a complete audit history.

**Acceptance Scenarios**:

1. **Given** an existing task, **When** the user updates the title or description, **Then** they receive an email with "Task Updated" status badge showing the new task details
2. **Given** an existing task, **When** the user deletes it, **Then** they receive an email with "Task Deleted" status badge and the deleted task's details for reference
3. **Given** rapid successive updates to the same task, **When** each update occurs, **Then** separate emails are sent for each update (full audit trail)

---

### Edge Cases

- What happens when the email API service is down or unreachable?
  - System logs the error but continues processing (non-blocking)
  - Task operation succeeds regardless of email status
- How does system handle invalid or bounced email addresses?
  - Email API handles delivery failures; system logs HTTP error responses
- What happens when tasks are created/updated/deleted in rapid succession?
  - Each operation triggers its own email notification independently
- How does system handle users without registered email addresses?
  - System requires email during registration; all users have email addresses
- What happens with very long task titles or descriptions?
  - Email template handles text wrapping and truncation gracefully

## Requirements

### Functional Requirements

- **FR-001**: System MUST send HTML email notification when a user creates a new task
- **FR-002**: System MUST send HTML email notification when a user marks a task as complete
- **FR-003**: System MUST send HTML email notification when a user updates task details
- **FR-004**: System MUST send HTML email notification when a user deletes a task
- **FR-005**: Email notifications MUST be sent asynchronously without blocking task operations
- **FR-006**: Email content MUST include task title, description, and status-appropriate messaging
- **FR-007**: Email template MUST be responsive and render correctly on mobile devices
- **FR-008**: System MUST use custom email API with Bearer token authentication
- **FR-009**: System MUST log all email sending attempts (success and failure)
- **FR-010**: Email sending failures MUST NOT cause task operations to fail

### Key Entities

- **Task Notification**: Represents an email notification event containing task_id, user_email, event_type (created/completed/updated/deleted), and task_data (title, description, timestamp)
- **Email Template**: HTML template with dynamic content including header, status badge, task details, and call-to-action
- **Notification Queue**: Background task queue for async email sending (FastAPI BackgroundTasks)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users receive task creation emails within 5 seconds of task creation 95% of the time
- **SC-002**: Email sending failures do not cause task operation failures (100% non-blocking)
- **SC-003**: Email templates render correctly across Gmail, Outlook, and mobile email clients
- **SC-004**: System can handle 100 task operations per minute without email backlog impacting performance
- **SC-005**: Users report successful email delivery in production environment

## Assumptions

1. Custom email API at `email.testservers.online/api/send` is reliable and available
2. Bearer token authentication is sufficient for email API authorization
3. All registered users have valid email addresses
4. Email API accepts HTML content and renders it correctly for recipients
5. Kubernetes secrets management is available for storing email API credentials
6. FastAPI BackgroundTasks provides adequate async task execution for email sending
7. Email delivery time of 5 seconds is acceptable for user experience

## Dependencies

### External Services
- Custom Email API: `https://email.testservers.online/api/send`
- User Database: PostgreSQL for user email lookup
- Email API Key: Bearer token stored as Kubernetes secret

### Technical Components
- FastAPI BackgroundTasks for async email sending
- httpx for async HTTP requests to email API
- HTML template system for email formatting
- Logging infrastructure for email send tracking

## Out of Scope

- Email unsubscribe functionality (users cannot opt-out of notifications)
- Email notification preferences/settings
- Bulk email operations (e.g., "email me all my tasks")
- Email attachment support
- Rich text or HTML in task descriptions (plain text only)
- Email reply-to functionality (emails are notifications only)
- Scheduled/digest emails (e.g., daily summary)
- Email open tracking or analytics
