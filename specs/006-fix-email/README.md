# Email Notification System - Quick Reference

## What Was Fixed

Switched from Gmail API OAuth2 (too complex) to custom email API with simple Bearer token authentication.

## Quick Links

- **Main Spec**: [spec.md](./spec.md) - Complete feature specification
- **Architecture**: [architecture.md](./architecture.md) - System design and diagrams
- **Configuration**: [configuration.md](./configuration.md) - Setup and deployment guide
- **Testing**: [testing.md](./testing.md) - Test strategies and examples
- **ADR**: [adr.md](./adr.md) - Architecture decision record

## Key Files

| File | Purpose |
|------|---------|
| `services/email-worker/app/email_service.py` | Email sending logic |
| `services/email-worker/app/subscribers.py` | Event handlers for all task events |
| `services/email-worker/app/config.py` | Configuration management |
| `services/email-worker/app/templates/task-crud.html` | Email template for CRUD events |
| `services/email-worker/app/main.py` | FastAPI app with Dapr subscriptions |

## Event Subscriptions

The email worker subscribes to 6 Dapr topics:

1. **task-created** → "Task Created: {title}"
2. **task-updated** → "Task Updated: {title}"
3. **task-completed** → "Task Completed: {title}"
4. **task-deleted** → "Task Deleted: {title}"
5. **task-due-soon** → "Task Due Soon: {title}"
6. **recurring-task-due** → "Recurring Task Due: {title}"

## Quick Test

```bash
# Test email endpoint
curl https://api.testservers.online/test-email

# Create a task (triggers email)
curl -X POST https://api.testservers.online/api/tasks \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Email", "description": "Check your inbox!"}'
```

Check inbox: `n00bi2761@gmail.com`

## Environment Variables

```bash
EMAIL_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
EMAIL_API_URL=https://email.testservers.online/api/send
MAIL_FROM=noreply@hackathon2.testservers.online
```

## Deployment Commands

```bash
# Build
docker build -t email-worker:v3 services/email-worker

# Push
docker push registry.digitalocean.com/hackathon2/email-worker:v3

# Deploy
kubectl set image deployment/email-worker \
  email-worker=registry.digitalocean.com/hackathon2/email-worker:v3

# Verify
kubectl logs -f deployment/email-worker
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| IP not whitelisted | Whitelist in email service control panel |
| Unauthorized | Check EMAIL_KEY secret |
| No email received | Check pod logs for errors |
| Dapr error | Verify sidecar is injected |

## Architecture Diagram

```
Frontend → Backend → Dapr Pub/Sub → Email Worker → Email API → User Inbox
```

## Status

✅ Implemented and deployed
✅ All 6 event subscriptions working
✅ Test email successful
✅ Production URL: https://hackathon2.testservers.online

## Next Steps

1. Monitor email delivery success rate
2. Add retry logic for failed emails
3. Implement email queue for high volume
4. Add email preferences per user
