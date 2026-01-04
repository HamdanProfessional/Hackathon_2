#!/bin/bash
TOKEN=$(curl -s -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"test1234"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

echo "Token obtained: ${TOKEN:0:20}..."

# Get the backend pod name
POD=$(kubectl get pods -n default -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
echo "Pod: $POD"

# Clear logs and make request
echo "Clearing old logs..."
kubectl logs -n default $POD -c backend --tail=0 > /dev/null

echo "Creating task..."
kubectl exec -n default $POD -c backend -- sh -c "curl -s -X POST http://localhost:8000/api/tasks \
  -H \"Authorization: Bearer $TOKEN\" \
  -H \"Content-Type: application/json\" \
  -d '{\"title\":\"DIRECT POD TEST\",\"description\":\"Testing direct to pod\",\"priority_id\":2}'"

echo ""
echo "Checking logs..."
kubectl logs -n default $POD -c backend --tail=30 | grep -i "debug\|event\|direct"
