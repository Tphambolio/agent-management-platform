# Deploy Agent Management Platform Online

## Current Issues
- Reports are "nonsense" because container has no API keys
- Agent skills system not working (no ANTHROPIC_API_KEY)
- No real web research (no BRAVE_API_KEY)
- System running locally, needs to be online

## Deployment Plan

### Step 1: Deploy Backend to Render
```bash
# Push code to GitHub (already done)
git push origin main

# Deploy to Render web service
# Service URL: https://agent-mgmt-backend.onrender.com (or similar)
```

### Step 2: Add Environment Variables on Render Dashboard
Navigate to: https://dashboard.render.com/web/[your-service-id]/env

Add these environment variables:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Your Claude API key
BRAVE_API_KEY=BSAxxxxx          # Your Brave Search API key
DATABASE_URL=postgresql://...   # Or use persistent disk for SQLite
PORT=8000
```

### Step 3: Deploy Frontend to Vercel
```bash
cd frontend
# Install Vercel CLI if needed
npm i -g vercel

# Deploy
vercel --prod

# Set environment variable:
VITE_API_URL=https://agent-mgmt-backend.onrender.com
```

### Step 4: Test Full System
1. Backend health: https://agent-mgmt-backend.onrender.com/health
2. Load agents: POST /api/agents
3. Create task: POST /api/tasks
4. Verify report has:
   - Real web research results
   - Scientific journal format
   - Python code blocks
   - Code extracted and added to agent genome

## What This Will Fix
✅ Real web research via Brave API
✅ Agent skills loaded from genome files
✅ Scientific reports with executable code
✅ Automatic code learning
✅ Both frontend and backend online and connected
✅ No more "nonsense" reports

## Next Steps
You need to:
1. Get your ANTHROPIC_API_KEY (from console.anthropic.com)
2. Get your BRAVE_API_KEY (from brave.com/search/api)
3. Choose: Deploy to existing Render service or create new one?
