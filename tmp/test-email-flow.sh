#!/bin/bash

EMAIL="n00bi2761@gmail.com"
PASSWORD="test1234"
API_URL="https://api.testservers.online"

echo "=========================================="
echo "  Email Notification Flow Test"
echo "=========================================="
echo ""

# Step 1: Login
echo "Step 1: Logging in as $EMAIL"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
    echo "❌ Failed to get auth token"
    echo "   Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Got token: ${TOKEN:0:30}..."
echo ""

# Get backend pod name
BACKEND_POD=$(kubectl get pods -n default -l app.kubernetes.io/name=backend --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
EMAIL_POD=$(kubectl get pods -n production -l app.kubernetes.io/name=email-worker --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')

echo "Backend Pod: $BACKEND_POD"
echo "Email Worker Pod: $EMAIL_POD"
echo ""

# Step 2: Create a test task
echo "Step 2: Creating test task..."
TIMESTAMP=$(date +%s)
TASK_TITLE="Email Test Task $TIMESTAMP"

TASK_RESPONSE=$(curl -s -X POST "$API_URL/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"$TASK_TITLE\",\"description\":\"Testing email notifications from Kubernetes\",\"priority_id\":2}")

echo "Task response: $TASK_RESPONSE"
echo ""

# Step 3: Check backend logs for event publishing
echo "Step 3: Checking backend logs for event publishing..."
sleep 2
EVENT_LOGS=$(kubectl logs -n default $BACKEND_POD -c backend --tail=50 2>&1 | grep -i "\[EVENT\]")

if [ -n "$EVENT_LOGS" ]; then
    echo "✅ Found event logs:"
    echo "$EVENT_LOGS"
else
    echo "⚠️  No [EVENT] logs found - event publishing may not be working"
fi
echo ""

# Step 4: Check Dapr logs
echo "Step 4: Checking Dapr sidecar logs..."
DAPR_LOGS=$(kubectl logs -n default $BACKEND_POD -c daprd --tail=50 2>&1 | grep -i "publish\|topic")

if [ -n "$DAPR_LOGS" ]; then
    echo "✅ Found Dapr publish activity:"
    echo "$DAPR_LOGS"
else
    echo "⚠️  No Dapr publish logs found"
fi
echo ""

# Step 5: Check email worker logs
echo "Step 5: Checking email worker logs..."
sleep 2
EMAIL_LOGS=$(kubectl logs -n production $EMAIL_POD -c email-worker --tail=50 2>&1 | grep -i "task-created\|email sent\|received")

if [ -n "$EMAIL_LOGS" ]; then
    echo "✅ Found email worker logs:"
    echo "$EMAIL_LOGS"
else
    echo "⚠️  No email worker activity logs found"
fi
echo ""

# Step 6: Summary
echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo ""
echo "Check your inbox at $EMAIL for a task notification email!"
echo ""
echo "If you didn't receive an email, possible reasons:"
echo "  1. Event not published (check backend logs above)"
echo "  2. Email API down (https://email.testservers.online)"
echo "  3. Email worker not receiving events"
echo ""
echo "To manually check email API status:"
echo "  curl -s https://email.testservers.online/api/send -X POST \\"
echo "    -H \"Authorization: Bearer emailsrv-a8f3e2d1-9c7b-4f6a-8e3d-2b1c5a9f7e4d\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"to\":\"test@test.com\",\"is_html\":true,\"subject\":\"Test\",\"body\":\"Test\"}'"
echo ""
