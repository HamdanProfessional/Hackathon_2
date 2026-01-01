# Quickstart Guide: Email Notification System

**Feature**: 006-fix-email
**Last Updated**: 2025-12-27

## Prerequisites

- Kubernetes cluster access (DigitalOcean DOKS)
- kubectl configured
- Test user account (n00bi2761@gmail.com / test1234)
- Email API credentials (already configured)

## 1. Get Authentication Token

```bash
# Login and get JWT token
curl -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"test1234"}' | \
  jq -r '.access_token' > /tmp/token.txt

# Verify token
TOKEN=$(cat /tmp/token.txt)
echo "Token: ${TOKEN:0:50}..."
```

## 2. Test Task Creation Email

```bash
# Create a task (should trigger email)
TOKEN=$(cat /tmp/token.txt)
curl -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Email Notification",
    "description": "Testing task creation email",
    "priority_id": 2
  }' | jq

# Expected response:
# {
#   "id": 123,
#   "title": "Test Email Notification",
#   "description": "Testing task creation email",
#   "completed": false,
#   ...
# }
```

**Verify**: Check inbox at `n00bi2761@gmail.com` for email with subject "Task Created: Test Email Notification"

## 3. Test Task Completion Email

```bash
# First, get task ID from previous response
TASK_ID=123  # Replace with actual ID from creation

# Complete the task (should trigger email)
TOKEN=$(cat /tmp/token.txt)
curl -X PATCH "https://api.testservers.online/api/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN" | jq

# Expected response:
# {
#   "id": 123,
#   "completed": true,
#   ...
# }
```

**Verify**: Check inbox for congratulatory email with green "COMPLETED" badge

## 4. Test Task Update Email

```bash
# Update task title
TASK_ID=123
TOKEN=$(cat /tmp/token.txt)
curl -X PUT "https://api.testservers.online/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated: Test Email Notification",
    "description": "Updated description"
  }' | jq
```

**Verify**: Check inbox for "Task Updated" email with yellow status badge

## 5. Test Task Deletion Email

```bash
# Delete the task
TASK_ID=123
TOKEN=$(cat /tmp/token.txt)
curl -X DELETE "https://api.testservers.online/api/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"

# Expected response: 204 No Content
```

**Verify**: Check inbox for "Task Deleted" email with red status badge

## 6. Check Backend Logs

```bash
# View backend logs for email sending confirmation
kubectl logs -n default deployment/todo-backend --tail=50 | grep -E "\[EMAIL\]"

# Expected output:
# [EMAIL] Sending created email to n00bi2761@gmail.com for task 123
# [EMAIL] Successfully sent created email to n00bi2761@gmail.com
```

## 7. Common Issues

### Issue: No email received

**Debug Steps**:
1. Check backend logs: `kubectl logs -f deployment/todo-backend | grep EMAIL`
2. Verify token is valid: `echo $TOKEN | cut -d'.' -f2 | base64 -d`
3. Check task was created: `curl -H "Authorization: Bearer $TOKEN" https://api.testservers.online/api/tasks`
4. Verify email API is reachable: `curl https://email.testservers.online/api/send`

**Expected Log Output**:
```
[EMAIL] Scheduling background task for email notification
[EMAIL] Background task scheduled
[EMAIL] Sending created email to n00bi2761@gmail.com for task 123
[EMAIL] Successfully sent created email to n00bi2761@gmail.com
```

### Issue: Email API returns 401 Unauthorized

**Solution**: Verify EMAIL_API_KEY secret in Kubernetes
```bash
kubectl get secret todo-backend-secrets -n default -o jsonpath='{.data.email-api-key}' | base64 -d
```

### Issue: Task creation succeeds but no email log

**Possible Causes**:
1. BackgroundTasks not properly injected
2. Email function not imported
3. Exception caught and logged elsewhere

**Debug**: Check full backend logs
```bash
kubectl logs -f deployment/todo-backend --tail=100
```

## 8. Performance Testing

### Load Test: Multiple Task Creations

```bash
# Create 10 tasks rapidly
for i in {1..10}; do
  TOKEN=$(cat /tmp/token.txt)
  curl -X POST "https://api.testservers.online/api/tasks" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"Load Test $i\",\"description\":\"Testing $i\"}" &
done
wait

# Check emails arrived (should be 10 emails)
```

**Expected**: All 10 tasks created, all 10 emails sent, no task operation failures

## 9. Manual Email Template Testing

```python
# Test email template locally
import asyncio
from backend.app.utils.email_notifier import send_task_email

async def test_template():
    result = await send_task_email(
        email="n00bi2761@gmail.com",
        subject="Test Email Template",
        task_title="Test Task",
        task_description="Testing HTML template rendering",
        task_status="created"
    )
    print(f"Email sent: {result}")

asyncio.run(test_template())
```

## 10. Verify Email Rendering

### Supported Email Clients

| Client | Version | Status |
|--------|---------|--------|
| Gmail Web | Latest | ✅ Tested |
| Gmail Mobile | iOS/Android | ✅ Expected |
| Outlook Web | Latest | ✅ Expected |
| Outlook Desktop | 2019+ | ✅ Expected |
| Apple Mail | iOS/macOS | ✅ Expected |

### Email Features Verified

- ✅ Gradient header renders correctly
- ✅ Status badges display with correct colors
- ✅ Responsive on mobile devices
- ✅ Links are clickable
- ✅ Text wrapping works for long titles
- ✅ UTF-8 characters supported

## 11. Environment Variables

### Production (DigitalOcean)

```bash
# Email API Configuration
EMAIL_API_URL=https://email.testservers.online/api/send
EMAIL_API_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d

# App URL for email links
FRONTEND_URL=https://hackathon2.testservers.online
```

### Local Development

```bash
# Use production email API even in local development
EMAIL_API_URL=https://email.testservers.online/api/send
EMAIL_API_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
```

## 12. Deployment Verification

```bash
# Check deployment is using correct image
kubectl get deployment todo-backend -n default -o jsonpath='{.spec.template.spec.containers[0].image}'

# Expected output:
# registry.digitalocean.com/todo-chatbot-reg/todo-backend:direct-email-v1

# Check environment variables
kubectl exec -n default deployment/todo-backend -- env | grep EMAIL

# Expected output:
# EMAIL_API_URL=https://email.testservers.online/api/send
# EMAIL_API_KEY=<hidden>
```

## 13. Rollback Procedure

If email notifications cause issues:

```bash
# Rollback to previous image
kubectl rollout undo deployment/todo-backend -n default

# Verify rollback
kubectl rollout status deployment/todo-backend -n default
```

## 14. Monitoring

### Key Metrics to Monitor

```bash
# Email success rate (from logs)
kubectl logs deployment/todo-backend --since=1h | grep "Successfully sent" | wc -l
kubectl logs deployment/todo-backend --since=1h | grep "Failed to send" | wc -l

# Email sending duration (not directly available, estimated <5s)
# Backend response time should not be impacted by email sending
```

### Alerting Thresholds

- Email failure rate >10%: Investigate email API
- Email sending timeout >10s: Check email API availability
- Task operation failures: Check if email sending is blocking

## 15. Success Criteria Verification

- [x] Task creation triggers email to user's registered address
- [x] Task completion triggers congratulatory email
- [x] Task update triggers notification email
- [x] Task deletion triggers confirmation email
- [x] Email sending failures don't block task operations
- [x] HTML emails render correctly in Gmail
- [x] Backend logs show email sending attempts
- [x] Production deployment successful at https://api.testservers.online

## Next Steps

After verification:

1. Monitor email delivery for 24 hours
2. Check user feedback on email usefulness
3. Consider adding email preferences if users find notifications too frequent
4. Explore email analytics (open rate, click rate) if needed

## Support

For issues or questions:
- Check backend logs: `kubectl logs -f deployment/todo-backend`
- Review email API documentation
- Contact: n00bi2761@gmail.com (test user)
