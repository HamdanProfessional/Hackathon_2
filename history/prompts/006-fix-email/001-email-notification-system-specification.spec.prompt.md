---
id: 001
title: "email notification system specification"
stage: spec
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-fix-email
branch: 006-fix-email
user: Hamdan
command: /sp.specify fix email notifications
labels: ["spec", "email", "notifications", "task-crud", "event-driven"]
links:
  spec: specs/006-fix-email/spec.md
  contract: null
  ticket: null
  adr: specs/006-fix-email/adr.md
  pr: null
files:
  - specs/006-fix-email/spec.md
  - specs/006-fix-email/checklists/requirements.md
tests:
  - Specification created with all required sections
  - User stories defined (P1: Creation, P2: Completion, P3: Update/Delete)
  - Success criteria defined
  - Validation checklist created
---

## Prompt

Fix Email Notifications - Implement direct email notification system for Todo task CRUD operations using custom email API

CONTEXT:
The Todo application's email notification system was non-functional due to:
1. Gmail API OAuth2 complexity (redirect_uri_mismatch, testing mode restrictions)
2. SMTP port blocking by cloud provider (DigitalOcean blocks ports 25, 465, 587)
3. User requirement: No third-party API keys (SendGrid, Resend, etc.)

Solution: Switch to custom email API with simple Bearer token authentication at `https://email.testservers.online/api/send`

INSTRUCTIONS:

1. **Create Specification Document** (`specs/006-fix-email/spec.md`):
   - Goal: Implement direct email notifications for task CRUD operations
   - User Stories (prioritized):
     * P1: Task creation email notification (MVP)
     * P2: Task completion email notification
     * P3: Task update and delete notifications
   - Technical approach: FastAPI BackgroundTasks + direct HTTP calls
   - Non-blocking: Email failures don't impact task operations
   - Email templates: HTML with status badges

2. **Create Requirements Checklist** (`specs/006-fix-email/checklists/requirements.md`):
   - Email notification utility module
   - Integration with task API endpoints
   - HTML email templates
   - Error handling and logging
   - Kubernetes deployment configuration

TECHNICAL REQUIREMENTS:

## Email Service
- API Endpoint: `https://email.testservers.online/api/send`
- Authentication: `Authorization: Bearer <EMAIL_API_KEY>`
- Method: HTTP POST with JSON payload
- Supports HTML email content

## Event Types
- `task-created`: Send email when task is created
- `task-completed`: Send email when task is completed
- `task-updated`: Send email when task is updated
- `task-deleted`: Send email when task is deleted

## Email Templates
- HTML templates with embedded CSS
- Color-coded status badges (created, updated, completed, deleted)
- Responsive design
- Gradient header (purple theme)

## Non-Functional Requirements
- Reliability: Async email sending with error handling
- Performance: Non-blocking HTTP calls with httpx
- Security: API key stored as Kubernetes secret
- Scalability: Containerized deployment with rolling updates

## Acceptance Criteria
- Email worker successfully sends test email
- All 4 event types trigger email notifications
- Email templates render correctly with task data
- Deployed to Kubernetes cluster
- IP whitelisted for email API access

## Dependencies
- Custom Email API: `https://email.testservers.online/api/send`
- User Database: PostgreSQL for user email lookup
- Email API Key: Bearer token stored as Kubernetes secret

## Python Packages
- `httpx>=0.27.0`: Async HTTP client
- `fastapi`: Web framework
- `sqlalchemy`: Database ORM

DELIVERABLES:
1. Complete feature specification (`specs/006-fix-email/spec.md`)
2. Requirements validation checklist (`specs/006-fix-email/checklists/requirements.md`)
3. All mandatory spec sections complete
4. Success criteria measurable and technology-agnostic
5. User scenarios independently testable
