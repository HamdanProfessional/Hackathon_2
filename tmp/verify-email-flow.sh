#!/bin/bash
echo "=== Email Notification Verification ==="
echo ""
echo "1. Checking Dapr sidecar..."
POD=$(kubectl get pods -n default -l app.kubernetes.io/name=backend --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
CONTAINERS=$(kubectl get pod $POD -n default -o jsonpath='{.spec.containers[*].name}')
echo "   Pod: $POD"
echo "   Containers: $CONTAINERS"
if [[ "$CONTAINERS" == *"daprd"* ]]; then
    echo "   ✅ Dapr sidecar present"
else
    echo "   ❌ Dapr sidecar NOT found!"
fi
echo ""
echo "2. Checking DAPR_ENABLED env var..."
DAPR_ENV=$(kubectl get deployment todo-backend -n default -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="DAPR_ENABLED")].value}')
echo "   DAPR_ENABLED=$DAPR_ENV"
if [[ "$DAPR_ENV" == "true" ]]; then
    echo "   ✅ Dapr enabled"
else
    echo "   ❌ Dapr NOT enabled!"
fi
echo ""
echo "3. Checking pub/sub component..."
COMPONENT=$(kubectl get component todo-pubsub -n default 2>&1)
if [[ "$COMPONENT" == *"todo-pubsub"* ]]; then
    echo "   ✅ Pub/sub component found"
else
    echo "   ❌ Pub/sub component NOT found!"
fi
echo ""
echo "4. Checking email worker..."
EMAIL_POD=$(kubectl get pods -n production -l app.kubernetes.io/name=email-worker --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
echo "   Email Worker Pod: $EMAIL_POD"
if [[ -n "$EMAIL_POD" ]]; then
    echo "   ✅ Email worker running"
    echo ""
    echo "5. Testing email endpoint..."
    RESULT=$(kubectl exec -n production $EMAIL_POD -c email-worker -- curl -s -X POST http://localhost:8003/test-email 2>&1)
    if [[ "$RESULT" == *"success"* ]]; then
        echo "   ✅ Test email sent successfully"
    else
        echo "   ❌ Test email failed: $RESULT"
    fi
else
    echo "   ❌ Email worker NOT running!"
fi
echo ""
echo "6. Enhanced logging is enabled in backend"
echo "   Look for [EVENT] tags when tasks are created"
echo ""
echo "=== Verification Complete ==="
echo ""
echo "Next: Create a task at https://hackathon2.testservers.online"
echo "Then run: kubectl logs -n default $POD -c backend --tail=50 | grep EVENT"
