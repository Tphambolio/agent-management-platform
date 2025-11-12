# 🚀 Deploy Agent Management Platform - Step by Step

## Quick Deploy (10 Minutes)

### STEP 1: Deploy Backend to Render (5 min)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign in (or create account if needed)

2. **Create New Web Service**
   - Click **"New +"** button → Select **"Web Service"**

3. **Connect Repository**
   - Connect your GitHub account if not already
   - Select repository: `Tphambolio/wildfire-simulator-v2`
   - Branch: `dashboard-focused`

4. **Configure Service**
   ```
   Name: agent-management-api
   Region: (Choose closest to you)
   Branch: dashboard-focused
   Root Directory: agent-management-platform/backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Add PostgreSQL Database**
   - Scroll down to "Add Database"
   - Click "New Database"
   - OR: Go to dashboard → "New +" → "PostgreSQL"
   - Name it: `agent-management-db`
   - This will auto-add `DATABASE_URL` to your web service

6. **Add Environment Variable**
   - In your web service settings, go to "Environment"
   - Add variable:
     ```
     Key: AGENTS_DIR
     Value: /opt/render/project/src/.agents
     ```

7. **Deploy!**
   - Click "Create Web Service"
   - Wait 2-3 minutes for deployment
   - Copy your backend URL (e.g., `https://agent-management-api.onrender.com`)

### STEP 2: Deploy Frontend to Vercel (2 min)

**Option A: Vercel CLI (Fastest)**

```bash
cd /home/rpas/wildfire-simulator-v2/agent-management-platform/frontend

# Set backend URL (use your Render URL from Step 1)
echo "VITE_API_URL=https://your-backend.onrender.com" > .env.production

# Install Vercel CLI if not installed
npm install -g vercel

# Deploy!
vercel --prod
```

**Option B: Vercel Dashboard**

1. Go to: https://vercel.com
2. Click "Add New..." → "Project"
3. Import: `Tphambolio/wildfire-simulator-v2`
4. Configure:
   ```
   Framework Preset: Vite
   Root Directory: agent-management-platform/frontend
   Build Command: npm run build
   Output Directory: dist
   ```
5. Add Environment Variable:
   ```
   Key: VITE_API_URL
   Value: https://your-backend.onrender.com
   ```
6. Click "Deploy"

### STEP 3: Test Your Deployment

```bash
# Test backend
curl https://your-backend.onrender.com/health
curl https://your-backend.onrender.com/api/agents

# Sync your 16 agents
curl -X POST https://your-backend.onrender.com/api/agents/sync

# Open frontend
# Visit: https://your-frontend.vercel.app
```

## 🎯 You're Live!

**Your Agent Management Platform is now online:**

- 🌐 **Dashboard**: https://your-frontend.vercel.app
- 🔌 **API**: https://your-backend.onrender.com
- 📚 **API Docs**: https://your-backend.onrender.com/docs
- 💬 **WebSocket**: wss://your-backend.onrender.com/ws

## ⚡ Quick Commands

```bash
# Get all agents
curl https://your-backend.onrender.com/api/agents

# Create a task
curl -X POST https://your-backend.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "performance-agent",
    "project_id": "wildfire-simulator",
    "title": "Optimize performance",
    "description": "Review critical paths",
    "priority": 3
  }'

# Get platform stats
curl https://your-backend.onrender.com/api/stats
```

## 🔧 Troubleshooting

**Backend not starting?**
- Check logs in Render dashboard
- Verify `DATABASE_URL` is set (should be auto-added)
- Make sure `AGENTS_DIR` environment variable is set

**Frontend can't connect?**
- Verify `VITE_API_URL` matches your Render backend URL
- Check browser console for CORS errors
- Backend might still be starting (first deploy takes 2-3 min)

**Agents not showing?**
- Run sync: `curl -X POST https://your-backend.onrender.com/api/agents/sync`
- Check that `.agents/` directory exists in your repo

## 📊 Monitor Your Deployment

**Render:**
- Logs: Dashboard → Your Service → Logs
- Metrics: Dashboard → Your Service → Metrics
- Events: Dashboard → Your Service → Events

**Vercel:**
- Deployments: Dashboard → Your Project → Deployments
- Analytics: Dashboard → Your Project → Analytics
- Logs: Click on any deployment → Runtime Logs

---

**That's it! Your agent workforce is now online! 🎉**
