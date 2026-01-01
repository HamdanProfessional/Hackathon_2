---
id: 002
title: "email notification implementation plan"
stage: plan
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-fix-email
branch: 006-fix-email
user: Hamdan
command: /sp.plan
labels: ["plan", "email", "architecture", "technical-design"]
links:
  spec: specs/006-fix-email/spec.md
  contract: specs/006-fix-email/contracts/email-api.yaml
  ticket: null
  adr: specs/006-fix-email/adr.md
  pr: null
files:
  - specs/006-fix-email/plan.md
  - specs/006-fix-email/research.md
  - specs/006-fix-email/data-model.md
  - specs/006-fix-email/quickstart.md
  - specs/006-fix-email/contracts/email-api.yaml
tests:
  - Technical research completed with decision documentation
  - Data model defined
  - Implementation phases outlined
  - API contracts created
  - Quickstart testing guide written
---

## Prompt

Create implementation plan for email notification system

CONTEXT:
Specification is complete at `specs/006-fix-email/spec.md`. Need to generate implementation plan with technical decisions, data model, and API contracts.

INSTRUCTIONS:

1. **Generate Research Document** (`specs/006-fix-email/research.md`):
   - Email service provider evaluation (Gmail, SMTP, SendGrid vs Custom API)
   - Async email sending pattern evaluation (BackgroundTasks, Celery, Dapr)
   - Email template strategy evaluation (Jinja2 vs Inline HTML)
   - Error handling strategy evaluation
   - HTTP client choice evaluation
   - Document all decisions with rationale and alternatives considered

2. **Generate Data Model Document** (`specs/006-fix-email/data-model.md`):
   - Email notification event structure
   - Email API request format
   - Email template context variables
   - HTML email template structure
   - Data flow diagrams
   - State transitions
   - Validation rules

3. **Generate Implementation Plan** (`specs/006-fix-email/plan.md`):
   - Technical context (Python 3.13+, FastAPI, httpx)
   - Constitution check (stateless, error handling, security)
   - Project structure (backend modifications)
   - Phase 0: Research decisions
   - Phase 1: Design & contracts
   - Phase 2: Implementation overview
   - Component specifications
   - Deployment strategy

4. **Generate Quickstart Guide** (`specs/006-fix-email/quickstart.md`):
   - Prerequisites
   - Authentication setup
   - Test procedures for each event type
   - Backend log verification
   - Common issues and solutions
   - Performance testing
   - Monitoring guidance

5. **Generate API Contract** (`specs/006-fix-email/contracts/email-api.yaml`):
   - OpenAPI 3.0 specification
   - POST /send endpoint
   - Request/response schemas
   - Authentication requirements
   - Error responses

TECHNICAL APPROACH:

## Core Decision: Direct API Calls (Bypassing Dapr Pub/Sub)
- Previous attempt with Dapr pub/sub failed due to DNS issues and namespace complexity
- Direct HTTP calls to email API simpler and more reliable
- FastAPI BackgroundTasks provides async execution

## Email Sending Pattern
```python
async def _send_email_notification(event_type: str, task_data: Dict, user_email: str):
    # Send email via custom API
    # Log success/failure
    # Never raise exceptions (non-blocking)
```

## Modified Endpoints
- POST /api/tasks (create)
- PUT /api/tasks/{id} (update)
- PATCH /api/tasks/{id}/complete (complete)
- DELETE /api/tasks/{id} (delete)

DELIVERABLES:
1. Research document with 6 technical decisions
2. Data model with email event structures
3. Implementation plan with phases
4. Quickstart testing guide
5. OpenAPI contract for email API
