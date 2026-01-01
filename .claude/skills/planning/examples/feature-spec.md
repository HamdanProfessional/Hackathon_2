# Feature Specification Template

Complete feature spec with user stories and acceptance criteria.

## Feature: [Feature Name]

## Overview

[2-3 sentence description]

## User Stories

- **US-1**: As a [user type], I want [goal], so that [benefit]
- **US-2**: As a [user type], I want [goal], so that [benefit]

## Acceptance Criteria

- [ ] **AC-1**: [Testable criterion]
- [ ] **AC-2**: [Testable criterion]

## Data Model (Backend)

### New Tables Required

- **Model Name**: [e.g., Task, Comment]
  - `id`: Integer (Primary Key)
  - `user_id`: UUID (Foreign Key)
  - `[field]`: [Type]
  - `created_at`: DateTime
  - `updated_at`: DateTime

### Relationships

- [Describe relationships]

### Indexes

- Index on `user_id` for user isolation

## API Endpoints

### 1. [Endpoint Name]

- **Method**: GET/POST/PUT/DELETE
- **Path**: `/api/{user_id}/[resource]`
- **Auth**: Required (JWT)

**Request Body**:
```json
{
  "field": "value"
}
```

**Response (200)**:
```json
{
  "id": 1,
  "field": "value"
}
```

**Errors**:
- `400`: Validation error
- `401`: Unauthorized
- `404`: Not found

## UI Requirements

### Key Screens

1. **[Screen Name]**:
   - Description: [What user sees]
   - Actions: [What user can do]

### Components Needed

- [Component 1]: [Purpose]
- [Component 2]: [Purpose]

## Dependencies & Integration

- **Existing Features**: [List dependencies]
- **Database Schema**: [Changes needed]
- **Authentication**: [How auth integrated]

## Non-Functional Requirements

- **Performance**: [Response time requirements]
- **Security**: [Data validation, authorization]
- **Accessibility**: [WCAG compliance]

## Implementation Phases

1. **Phase 1**: Backend models and API
2. **Phase 2**: Frontend UI components
3. **Phase 3**: Integration and testing
