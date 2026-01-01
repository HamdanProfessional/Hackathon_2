# ADR 006: Switch to Custom Email API

## Status
Accepted

## Date
2025-12-27

## Context

The Todo application requires email notifications for task events. Initial implementation attempts encountered significant blockers:

### Attempt 1: Gmail API with OAuth2
**Problem**: OAuth2 flow too complex for this use case
- Redirect URI mismatch errors
- App in "Testing" mode requires adding test users
- User feedback: "BRO I WANT EMAIL BUT GOOGLE IS GOING GAY AND I DONT WANT TO USE API KEYS FOR EMAILING"

### Attempt 2: SendGrid
**Problem**: User explicitly rejected third-party API keys
- User requirement: "no api key alternate"

### Attempt 3: SMTP
**Problem**: Cloud provider blocks SMTP ports
- DigitalOcean blocks ports 25, 465, 587
- No alternative SMTP ports available

## Decision

Use custom email API at `email.testservers.online` with Bearer token authentication.

**Key Factors**:
1. Simple HTTP-based API (no complex OAuth flows)
2. Pre-provisioned API key (no third-party service signup)
3. User-controlled infrastructure (full whitelisting control)
4. Async-compatible (works with FastAPI)

## Consequences

### Positive
- **Simplicity**: Single HTTP POST request to send email
- **No OAuth complexity**: Bearer token authentication
- **User control**: IP whitelisting for security
- **Reliability**: Custom service, no rate limiting from third-party
- **Async-friendly**: Non-blocking with httpx

### Negative
- **Vendor lock-in**: Custom service, need to maintain availability
- **Limited documentation**: Less comprehensive than SendGrid/Gmail APIs
- **Single point of failure**: If email service goes down, notifications fail

### Mitigations
- Monitor email service health
- Consider fallback to alternative email service
- Log all email failures for debugging

## Implementation

### API Specification
```
POST https://email.testservers.online/api/send
Headers:
  Authorization: Bearer <EMAIL_KEY>
  Content-Type: application/json
Body:
  {
    "to": "recipient@example.com",
    "subject": "Email subject",
    "body": "<html>Email body</html>"
  }
Response:
  200 OK on success
  401 Unauthorized if invalid token
  403 Access denied if IP not whitelisted
```

### Configuration
```python
EMAIL_KEY=emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d
EMAIL_API_URL=https://email.testservers.online/api/send
MAIL_FROM=noreply@hackathon2.testservers.online
```

## Alternatives Considered

### 1. Gmail API with OAuth2
**Rejected**: Too complex, requires OAuth flow, redirect URI configuration

### 2. SendGrid
**Rejected**: User explicitly rejected API keys from third-party services

### 3. Resend
**Rejected**: Same as SendGrid - requires API key management

### 4. Mailgun
**Rejected**: Same as SendGrid - requires API key management

### 5. SMTP with DigitalOcean
**Rejected**: Ports 25, 465, 587 blocked by cloud provider

## References

- Email API: https://email.testservers.online
- Dapr Pub/Sub: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- Issue discussion: Session summary from 2025-12-27
