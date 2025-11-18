#!/bin/bash
# Quick deploy script for Railway.app

set -e

echo "🚀 Deploying Agent Management Platform to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "📝 Logging into Railway..."
railway login

# Deploy Backend
echo ""
echo "🔧 Deploying Backend..."
cd backend
railway init --name agent-management-backend || railway link
railway up

# Get backend URL
echo ""
echo "🌐 Getting backend URL..."
BACKEND_URL=$(railway domain 2>/dev/null || echo "")

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  Could not auto-detect backend URL."
    echo "Please set it manually in Railway dashboard and update frontend/.env.production"
    read -p "Enter your backend URL (or press Enter to skip): " BACKEND_URL
fi

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
railway variables set HOST=0.0.0.0
railway variables set DEBUG=false
railway variables set PORT='$PORT'

if [ ! -z "$BACKEND_URL" ]; then
    # Create frontend .env.production
    echo ""
    echo "📝 Configuring frontend..."
    cd ../frontend
    echo "VITE_API_URL=https://$BACKEND_URL" > .env.production

    # Update CORS
    cd ../backend
    railway variables set CORS_ORIGINS="https://$BACKEND_URL,http://localhost:3000"
fi

echo ""
echo "✅ Backend deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Deploy frontend to Vercel:"
echo "   cd frontend && vercel --prod"
echo ""
echo "2. Or deploy frontend to Railway:"
echo "   cd frontend && railway init && railway up"
echo ""
echo "3. Your backend is available at: https://$BACKEND_URL"
echo "   API Docs: https://$BACKEND_URL/docs"
echo ""
echo "4. (Optional) Set ANTHROPIC_API_KEY for real LLM execution:"
echo "   railway variables set ANTHROPIC_API_KEY=sk-your-key"
echo ""
