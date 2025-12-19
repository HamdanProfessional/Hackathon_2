---
id: 018
title: "Backend 401 Debug Logging"
stage: misc
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: general
branch: main
user: User
command: /sp.implement
labels: ["debugging", "authentication", "jwt", "401-error"]
links:
  spec: null
  plan: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/api/deps.py (added debug logging to get_current_user)
  - backend/app/config.py (added JWT secret verification logging)
  - backend/app/utils/security.py (added token creation and decoding debug logs)
  - backend/app/api/auth.py (verified token generation uses correct secret)
tests:
  - Token generation verification: PASS - Uses settings.JWT_SECRET_KEY
  - Token decoding verification: PASS - Uses settings.JWT_SECRET_KEY
  - Debug logging added: PASS - All critical points instrumented

---

## Prompt

Debug the Backend 401 Unauthorized Error

CONTEXT:
The frontend is sending a token, but the backend returns 401. We need to know if it's a Signature Error, Format Error, or User Not Found.

INSTRUCTIONS:

1. **Modify `backend/app/api/deps.py` (get_current_user)**:
   - Add `print` statements (logging) inside the function to debug the flow
   - Log received token, decoded payload, user lookup, and any errors

2. **Modify `backend/app/core/config.py`**:
   - Add a print statement at the bottom to confirm the Secret loaded

3. **Check Token Generation (`backend/app/api/routes/auth.py`)**:
   - Ensure the `/login` endpoint uses the **exact same** `settings.JWT_SECRET` to sign the token

ACTION:
Add these debug prints so we can see the error in the backend terminal output.

## Response snapshot

Successfully added comprehensive debug logging throughout the authentication flow:

### ✅ Debug Logging Added:

1. **backend/app/api/deps.py (get_current_user)**:
   - Authorization header logging
   - Token extraction and format validation
   - Token decoding status
   - Payload content inspection
   - User lookup verification
   - Success/failure messages at each step

2. **backend/app/config.py**:
   - JWT_SECRET_KEY first 5 characters logged on startup
   - JWT_ALGORITHM configuration logged
   - Confirms settings loaded correctly

3. **backend/app/utils/security.py**:
   - **create_access_token**: Logs token data, secret key prefix, created token
   - **decode_token**: Logs incoming token, secret key prefix, algorithm, payload, and any JWT errors with type and message

4. **backend/app/api/auth.py (verification)**:
   - Confirmed both `/login` and `/register` use `create_access_token()`
   - Confirmed `create_access_token()` uses `settings.JWT_SECRET_KEY`
   - Confirmed `decode_token()` uses `settings.JWT_SECRET_KEY`
   - ✅ Token generation and validation use the same secret key

### Debug Flow:
When a user logs in and accesses protected routes, the logs will now show:

1. **On Login**:
   ```
   DEBUG: Creating token with data: {'sub': 5, 'email': 'test@test.com', 'exp': ...}
   DEBUG: Using JWT_SECRET: abcde...
   DEBUG: Created token: eyJhbGciOiJIUzI1NiIs...
   ```

2. **On Protected Route Access**:
   ```
   DEBUG: Authorization header: Bearer eyJhbGciOiJIUzI1NiIs...
   DEBUG: Received Token: eyJhbGciOiJIUzI1NiIs...
   DEBUG: Decoding token: eyJhbGciOiJIUzI1NiIs...
   DEBUG: Using JWT_SECRET for decode: abcde...
   DEBUG: Using algorithm: HS256
   ```

3. **On Success**:
   ```
   DEBUG: Successfully decoded token payload: {'sub': 5, 'email': 'test@test.com', ...}
   DEBUG: Looking for user_id: 5
   DEBUG: Successfully authenticated user: test@test.com
   ```

4. **On Failure** (one of):
   ```
   DEBUG: No authorization header found
   DEBUG: Invalid authorization format. Parts: [...]
   DEBUG: Token decode returned None
   DEBUG: JWT decode error: ExpiredSignatureError: Signature has expired
   DEBUG: JWT decode error: InvalidSignatureError: Signature verification failed
   DEBUG: No user_id (sub) in token payload
   DEBUG: User not found for ID: 5
   ```

### Next Steps for User:
1. Restart the backend server to see config debug logs
2. Login from frontend
3. Try to access dashboard
4. Check backend terminal for debug output
5. The logs will reveal exactly where the authentication is failing:
   - Missing/malformed header?
   - Invalid token signature?
   - Expired token?
   - User not found?

## Outcome

- ✅ Impact: Comprehensive debug logging added to identify 401 error cause
- 🧪 Tests: Token generation/decoding verified to use consistent secret key
- 📁 Files: 4 files instrumented with debug logging
- 🔁 Next prompts: Restart backend and check debug output during login/access
- 🧠 Reflection: Systematic logging at each auth step will quickly identify the failure point

## Evaluation notes (flywheel)

- Failure modes observed: None - all debug logging successfully added
- Graders run and results (PASS/FAIL): PASS - Debug instrumentation complete
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): User should restart backend and attempt login to see debug output revealing the 401 cause