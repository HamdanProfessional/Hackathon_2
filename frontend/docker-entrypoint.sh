#!/bin/sh
set -e

# Generate config.json from environment variable at runtime
# This allows changing the backend URL without rebuilding the image
if [ -n "$NEXT_PUBLIC_API_URL" ]; then
  echo "Generating config.json with NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL"
  cat > /app/public/config.json << EOF
{
  "NEXT_PUBLIC_API_URL": "$NEXT_PUBLIC_API_URL"
}
EOF
else
  echo "Warning: NEXT_PUBLIC_API_URL not set, using default"
  cat > /app/public/config.json << EOF
{
  "NEXT_PUBLIC_API_URL": "http://localhost:8000"
}
EOF
fi

# Execute the main command
exec "$@"
