#!/bin/bash

echo "=== Getting auth token ==="
LOGIN_RESPONSE=$(curl -s -X POST "https://api.testservers.online/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"n00bi2761@gmail.com","password":"testpass123"}')

echo "Login response: ${LOGIN_RESPONSE:0:100}..."

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:20}..."

echo ""
echo "=== Creating task ==="
TASK_RESPONSE=$(curl -s -X POST "https://api.testservers.online/api/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Email Test Task $(date +%s)\",\"description\":\"Testing email notifications\",\"priority_id\":2}")

echo "Task response: $TASK_RESPONSE"
