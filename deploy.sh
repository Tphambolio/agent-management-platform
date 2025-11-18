#!/bin/bash
# Agent Management Platform - Automated Deployment Script

set -e

echo "════════════════════════════════════════════════════════════"
echo "  🚀 Agent Management Platform - Cloud Deployment"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}⚠️  Render CLI not found. We'll use web interface instead.${NC}"
    RENDER_CLI=false
else
    RENDER_CLI=true
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${BLUE}Installing Vercel CLI...${NC}"
    npm install -g vercel
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  STEP 1: Deploy Backend to Render"
echo "════════════════════════════════════════════════════════════"
echo ""

if [ "$RENDER_CLI" = true ]; then
    echo "Using Render CLI..."
    # Deploy via CLI
else
    echo "📋 Follow these steps to deploy backend:"
    echo ""
    echo "1. Go to: https://dashboard.render.com"
    echo "2. Click 'New +' → 'Web Service'"
    echo "3. Connect your GitHub repository: Tphambolio/wildfire-simulator-v2"
    echo "4. Configure:"
    echo "   - Name: agent-management-api"
    echo "   - Branch: dashboard-focused"
    echo "   - Root Directory: agent-management-platform/backend"
    echo "   - Build Command: pip install -r requirements.txt"
    echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
    echo "   - Environment: Python 3.10"
    echo ""
    echo "5. Add PostgreSQL database:"
    echo "   - Click 'New +' → 'PostgreSQL'"
    echo "   - Name: agent-management-db"
    echo "   - Connect to your web service"
    echo ""
    echo "6. Environment Variables (auto-added by Render):"
    echo "   - DATABASE_URL (from PostgreSQL)"
    echo "   - AGENTS_DIR=/opt/render/project/src/.agents"
    echo ""
    
    read -p "Press ENTER when backend is deployed and you have the URL..."
fi

echo ""
read -p "Enter your Render backend URL (e.g., https://agent-management-api.onrender.com): " BACKEND_URL

# Validate URL
if [[ ! $BACKEND_URL =~ ^https?:// ]]; then
    echo -e "${YELLOW}⚠️  Adding https:// to URL${NC}"
    BACKEND_URL="https://$BACKEND_URL"
fi

echo -e "${GREEN}✓${NC} Backend URL: $BACKEND_URL"
echo ""

echo "════════════════════════════════════════════════════════════"
echo "  STEP 2: Deploy Frontend to Vercel"
echo "════════════════════════════════════════════════════════════"
echo ""

cd frontend

# Update environment variable
echo "VITE_API_URL=$BACKEND_URL" > .env.production

echo -e "${BLUE}Deploying to Vercel...${NC}"
echo ""

# Deploy to Vercel
vercel --prod --yes

FRONTEND_URL=$(vercel --prod 2>&1 | grep -o 'https://[^[:space:]]*' | tail -1)

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}Backend API:${NC}  $BACKEND_URL"
echo -e "${GREEN}Frontend:${NC}     $FRONTEND_URL"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎯 Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test your backend:"
echo "   curl $BACKEND_URL/health"
echo "   curl $BACKEND_URL/api/agents"
echo ""
echo "2. Open your dashboard:"
echo "   $FRONTEND_URL"
echo ""
echo "3. View API docs:"
echo "   $BACKEND_URL/docs"
echo ""
echo "4. Sync agents (if needed):"
echo "   curl -X POST $BACKEND_URL/api/agents/sync"
echo ""
echo "════════════════════════════════════════════════════════════"
