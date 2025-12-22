#!/bin/bash
# Automated Vercel frontend deployment

set -e

PROJECT_DIR="${1:-.}"
PROJECT_NAME="${2:-frontend}"

echo "🚀 Deploying $PROJECT_NAME to Vercel..."

cd "$PROJECT_DIR"

# Check for .env.local
if [ -f ".env.local" ]; then
    echo "⚠️  Warning: .env.local found. Vercel uses environment variables from dashboard."
    echo "   Make sure to set vars in Vercel dashboard or use vercel env add"
fi

# Deploy to production
echo "📦 Building and deploying..."
vercel --prod

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "  1. Set environment variables: vercel env add NEXT_PUBLIC_API_URL production"
echo "  2. Check deployment status: vercel ls"
