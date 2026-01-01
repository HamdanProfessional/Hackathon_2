# Email Notification System - Quick Reference

## What Was Fixed

Switched from Dapr pub/sub with email worker to **direct email notifications** using FastAPI BackgroundTasks, bypassing DNS and namespace issues.

## Quick Links

- **Main Spec**: [spec.md](./spec.md) - Feature specification with user stories
- **Implementation Plan**: [plan.md](./plan.md) - Technical decisions and architecture
- **Task Breakdown**: [tasks.md](./tasks.md) - 33 actionable implementation tasks
- **Research**: [research.md](./research.md) - Technical decisions and alternatives
- **Data Model**: [data-model.md](./data-model.md) - Email event structures
- **Quickstart**: [quickstart.md](./quickstart.md) - Testing and deployment guide
- **API Contract**: [contracts/email-api.yaml](./contracts/email-api.yaml) - OpenAPI specification

## Key Files

| File | Purpose |
|------|---------|
| `backend/app/utils/email_notifier.py` | Direct email sending utility (NEW) |
| `backend/app/api/tasks.py` | Modified to send emails on CRUD operations |
| `k8s/backend/deployment.yaml` | EMAIL_API_URL and EMAIL_API_KEY env vars |
| `k8s/backend/secrets.yaml` | EMAIL_API_KEY secret |

## Email Notification Events

The backend sends emails for 4 task events:

1. **Task Created** → "Task Created: {title}"
2. **Task Updated** → "Task Updated: {title}"
3. **Task Completed** → "Task Completed: {title}"
4. **Task Deleted** → "Task Deleted: {title}"

## Implementation Details

### Email Sending Pattern
- **FastAPI BackgroundTasks** - Async, non-blocking email sends
- **Direct HTTP calls** - Bypasses Dapr pub/sub complexity
- **Custom Email API** - Simple Bearer token authentication

### Email Template Features
- HTML format with responsive design
- Color-coded status badges (green, yellow, blue, red)
- Purple gradient header
- Task details included
- Link to application

## Quick Test

```bash
# Get JWT token
TOKEN=$(curl -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"test1234"}' | jq -r '.access_token')

# Create a task (triggers email)
curl -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Email", "description": "Check your inbox!"}'

# Check backend logs
kubectl logs -n default deployment/todo-backend --tail=30 | grep EMAIL
```

Check inbox: `n00bi2761@gmail.com`

## Environment Variables

```bash
EMAIL_API_URL=https://email.testservers.online/api/send
EMAIL_API_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
```

## Deployment Commands

```bash
# Build
docker build -t todo-backend:direct-email-v1 backend/

# Tag
docker tag todo-backend:direct-email-v1 registry.digitalocean.com/todo-chatbot-reg/todo-backend:direct-email-v1

# Push
docker push registry.digitalocean.com/todo-chatbot-reg/todo-backend:direct-email-v1

# Deploy
kubectl set image deployment/todo-backend \
  backend=registry.digitalocean.com/todo-chatbot-reg/todo-backend:direct-email-v1 -n default

# Verify
kubectl rollout status deployment/todo-backend -n default
kubectl logs -f deployment/todo-backend -n default | grep EMAIL
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No email received | Check backend logs for `[EMAIL]` entries |
| Email send failed | Verify EMAIL_API_KEY in Kubernetes secrets |
| Task creation slow | Email sending is async, shouldn't block |
| Email template broken | Check `email_notifier.py` HTML template |

## Architecture Diagram

```
Frontend → Backend (FastAPI) → BackgroundTasks → Email API → User Inbox
                ↓
          TaskEventLog (audit)
```

## Backend Log Output

```
[EMAIL] Scheduling background task for email notification
[EMAIL] Background task scheduled
[EMAIL] Sending created email to n00bi2761@gmail.com for task 173
[EMAIL] Successfully sent created email to n00bi2761@gmail.com
```

## Status

✅ Implemented and deployed
✅ All 4 email notification events working
✅ Production URL: https://hackathon2.testservers.online
✅ Docker image: `direct-email-v1`
✅ Non-blocking email sends

## Spec-Kit Plus Documentation

This feature follows the Spec-Kit Plus workflow:

1. **Specification** - [spec.md](./spec.md) with 3 user stories (P1-P3)
2. **Plan** - [plan.md](./plan.md) with technical decisions
3. **Tasks** - [tasks.md](./tasks.md) with 33 actionable tasks
4. **Implementation** - Complete, tested, deployed

## PHR Files

See [history/prompts/006-fix-email/](../../history/prompts/006-fix-email/) for complete workflow documentation:
- `001-email-notification-system-specification.spec.prompt.md`
- `002-email-notification-implementation-plan.plan.prompt.md`
- `003-email-notification-task-breakdown.tasks.prompt.md`
- `004-email-notification-implementation.implement.prompt.md`

## Email Testing Checklist

- [x] Task creation sends email
- [x] Task completion sends congratulatory email
- [x] Task update sends notification email
- [x] Task deletion sends confirmation email
- [x] Email template renders correctly in Gmail
- [x] Email sending is non-blocking
- [x] Backend logs show email sending attempts
- [x] Kubernetes secrets configured correctly

## Previous Attempts (Archived)

❌ Gmail API with OAuth2 - Too complex, redirect_uri_mismatch
❌ Dapr pub/sub with email worker - DNS resolution issues
❌ SMTP - Blocked by DigitalOcean (ports 25, 465, 587)

## Success Criteria

- Users receive task creation emails within 5 seconds (95% of time)
- Email sending failures don't cause task operation failures (100%)
- Email templates render correctly across Gmail/Outlook/mobile
- System handles 100 task ops/minute without performance impact
- Production deployment stable with proper monitoring

## Next Steps

1. Monitor email delivery success rate in production
2. Add email open tracking (if needed)
3. Implement email preferences per user (optional)
4. Add email digest functionality (optional)
