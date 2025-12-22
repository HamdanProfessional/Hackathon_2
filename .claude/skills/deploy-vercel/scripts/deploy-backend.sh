#!/bin/bash
# Automated Vercel backend deployment

set -e

PROJECT_DIR="${1:-.}"
PROJECT_NAME="${2:-backend}"

echo "🚀 Deploying $PROJECT_NAME (FastAPI) to Vercel..."

cd "$PROJECT_DIR"

# Check requirements
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

if [ ! -f "vercel.json" ]; then
    echo "⚠️  Warning: vercel.json not found. Creating basic config..."
    cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/app/main.py"
    }
  ]
}
EOF
fi

# Deploy to production
echo "📦 Building and deploying..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "Required environment variables:"
echo "  DATABASE_URL"
echo "  JWT_SECRET"
echo "  GROQ_API_KEY (or other AI provider)"
echo ""
echo "Set them with: vercel env add <NAME> production"
