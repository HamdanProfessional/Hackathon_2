# Task Breakdown Template

Complete task breakdown with dependencies and estimates.

## Task Breakdown: [Feature Name]

### Task Properties

Each task includes:
- **Title**: Clear, actionable name
- **Description**: Detailed what/why/how
- **Acceptance Criteria**: Definition of done
- **Estimate**: Story points (Fibonacci: 1, 2, 3, 5, 8, 13)
- **Priority**: High/Normal/Low
- **Dependencies**: What must be done first
- **Category**: feature/bug/refactor/docs/testing

### Estimation Guidelines

| Points | Time | Complexity |
|--------|------|------------|
| 1 | 1-2 hours | Trivial |
| 2 | 2-4 hours | Simple |
| 3 | 4-8 hours | Moderate |
| 5 | 1-2 days | Complex |
| 8 | 2-3 days | Very Complex |
| 13 | 3-5 days | Extremely Complex |

## Tasks

### Task 1: [Task Name]
- **ID**: [FEAT-1]
- **Title**: [Clear name]
- **Description**: [What needs to be done]
- **Estimate**: [3] points
- **Priority**: [High]
- **Dependencies**: [None]
- **Category**: [feature]
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

### Task 2: [Task Name]
- **ID**: [FEAT-2]
- **Title**: [Clear name]
- **Description**: [What needs to be done]
- **Estimate**: [5] points
- **Priority**: [Normal]
- **Dependencies**: [FEAT-1]
- **Category**: [feature]
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

### Task 3: [Task Name]
- **ID**: [FEAT-3]
- **Title**: [Clear name]
- **Description**: [What needs to be done]
- **Estimate**: [2] points
- **Priority**: [Normal]
- **Dependencies**: [None]
- **Category**: [testing]
- **Acceptance Criteria**:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

## Sprint Planning

**Sprint 1** (Velocity: 20 points):
- Task 1 (3 points)
- Task 2 (5 points)
- Task 3 (2 points)
- Task 4 (5 points)
- Task 5 (5 points)
**Total**: 20 points

## Dependency Graph

```
Task 1 (3pts)
  |
  v
Task 2 (5pts)
  |
  v
Task 4 (5pts)

Task 3 (2pts) [parallel]
  |
  v
Task 5 (5pts)
```
