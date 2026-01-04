#!/bin/bash
echo "Creating task..."
TOKEN=$(curl -s -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"test1234"}' | \
  grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl -s -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Test Email $(date +%s)\",\"description\":\"Testing email notifications\",\"priority_id\":2}" > /dev/null

echo "Task created. Waiting 3 seconds..."
sleep 3

echo "Email worker logs:"
kubectl logs -n default email-worker-56c798cd74-w9fk7 -c email-worker --tail=20
