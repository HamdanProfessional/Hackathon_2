# Documentation - Reusable Templates

## README Template

```markdown
# [Project Name]

[One-line description]

## Overview

[2-3 paragraphs about the project]

## Features

- [Feature 1]
- [Feature 2]

## Tech Stack

### Backend
- [Framework and version]
- [Database]
- [Other tools]

### Frontend
- [Framework]
- [Language]
- [Styling]

## Installation

### Prerequisites

- [Requirement 1]
- [Requirement 2]

### Setup

```bash
# Installation commands
```

## Usage

[How to use the project]

## API Documentation

[Link to API docs or describe endpoints]

## Development

```bash
# Run tests
# Run linter
# Run build
```

## Deployment

[Deployment instructions]

## License

[License type]
```

## ADR Template

```markdown
# ADR-XXX: [Title]

**Status**: Proposed | Accepted | Rejected
**Date**: YYYY-MM-DD
**Decision Makers**: [Names]
**Tags**: #[tag1] #[tag2]

---

## Context

[Background and context]

**Problem Statement**:
[Clear description of the problem]

**Constraints**:
- [Constraint 1]
- [Constraint 2]

---

## Decision

[What decision was made]

**Chosen Option**: [Option name]

**Rationale**:
[Why this option was chosen]

---

## Options Considered

### Option 1: [Name]

**Description**: [Details]

**Pros**: [Advantages]

**Cons**: [Disadvantages]

---

## Consequences

**Positive**: [Benefits]

**Negative**: [Tradeoffs]

---

## Implementation

**Actions**:
1. [Step 1]
2. [Step 2]

**Testing**: [Testing strategy]

**Rollback**: [Rollback plan]
```

## API Docs Template

```markdown
# API Documentation

## Base URL

- Development: http://localhost:8000
- Production: https://api.example.com

## Authentication

[Auth description]

## Endpoints

### [Resource Name]

#### [Action] [Resource]
**[METHOD]** `/path`

[Description]

**Request**:
```json
{request body}
```

**Response 200**:
```json
{response}
```

**Errors**:
- `400`: Error description
- `401`: Error description
```

## PHR Template

```markdown
---
id: XXX
title: [Title]
stage: [green/red/refactor]
date: ISO date
surface: agent
model: model name
feature: feature name
branch: branch name
user: user name
command: command used
labels: [labels]
links:
  spec: spec link
  ticket: ticket link
  pr: pr link
files:
  - file1 (action)
  - file2 (action)
tests:
  - test file (status)
---

## Prompt

[User prompt]

## Response

[AI response summary]

## Outcome

- [ ] Impact: [What was accomplished]
- [ ] Tests: [Test results]
- [ ] Files: [Files modified]
- [ ] Next: [Next steps]

## Evaluation

[Notes on what worked/didn't work]
```
