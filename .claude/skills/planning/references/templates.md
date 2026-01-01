# Planning - Reusable Templates

## Implementation Plan Template

```markdown
# Implementation Plan: [Feature Name]

**Spec**: @specs/[feature]/spec.md
**Phase**: [Phase]
**Complexity**: [Simple/Moderate/Complex]
**Timeline**: [Duration]

---

## Overview

[2-3 sentence summary]

**Success Criteria**:
- [ ] [Criterion]
- [ ] [Criterion]

---

## Architecture

### Component Diagram

```
[Mermaid diagram or ASCII art]
```

### Component Responsibilities

**Frontend**:
- Location: `frontend/app/[feature]/`
- Components: [List]

**Backend**:
- Location: `backend/app/routers/[feature].py`
- Endpoints: [List]

---

## Data Model

### Tables

| Table | Columns | Indexes |
|-------|---------|---------|
| [Name] | [Columns] | [Indexes] |

---

## API Design

### Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /[resource] | JWT | List items |
| POST | /[resource] | JWT | Create item |

---

## Tasks

### Task 1: [Name]
- **Points**: [3]
- **Dependencies**: [None]
- **Acceptance**:
  - [ ] [Done criteria]

---

## Testing

- **Unit**: [What to test]
- **Integration**: [What to test]
- **E2E**: [What to test]

---

## Risks

| Risk | Mitigation |
|------|------------|
| [Risk] | [Strategy] |
```

## Feature Spec Template

```markdown
# Feature: [Name]

## Overview

[Description]

## User Stories

- **US-1**: As a [user], I want [goal], so that [benefit]

## Acceptance Criteria

- [ ] **AC-1**: [Testable criterion]
- [ ] **AC-2**: [Testable criterion]

## Data Model

### [TableName]
- `field`: type (constraints)

## API

### [Endpoint]
**Method**: GET/POST/...
**Path**: `/path`
**Auth**: JWT
**Request**: [body]
**Response**: [body]

## UI

### Screens
- [Screen]: [description]

## Dependencies

- [Dependency]
- [Integration]

## NFRs

- Performance: [requirements]
- Security: [requirements]

## Implementation

1. [Phase 1]
2. [Phase 2]
3. [Phase 3]
```

## Task Template

```markdown
### Task: [Title]

- **ID**: [XXX-1]
- **Title**: [Clear name]
- **Description**: [What and why]
- **Story Points**: [1,2,3,5,8,13]
- **Priority**: [High/Normal/Low]
- **Dependencies**: [Task IDs]
- **Category**: [feature/bug/refactor/test/docs]

### Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

### Definition of Done

- [ ] Code written
- [ ] Tests passing
- [ ] Code reviewed
- [ ] Documentation updated
```
