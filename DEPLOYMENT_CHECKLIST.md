# ✅ Agent Management Platform - Deployment Checklist

## 🎯 What You Need

- ✅ GitHub repository with code (DONE - just pushed!)
- ✅ Render.com account (free tier works)
- ✅ Vercel account (free tier works)
- ✅ 10 minutes of time

---

## 📋 BACKEND DEPLOYMENT (Render.com)

### Step 1: Create Render Account
1. Go to: https://render.com
2. Sign up with GitHub (easiest)

### Step 2: Deploy Backend
1. **In Render Dashboard:**
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository:**
   - Select: `Tphambolio/wildfire-simulator-v2`
   - Branch: `dashboard-focused`

3. **Configure:**
   ```
   Name:              agent-management-api
   Region:            Oregon (US West) or closest to you
   Branch:            dashboard-focused
   Root Directory:    agent-management-platform/backend
   Runtime:           Python 3
   Build Command:     pip install -r requirements.txt
   Start Command:     uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Instance Type:     Free
   ```

4. **Environment Variables:**
   Click "Advanced" → Add Environment Variable:
   ```
   AGENTS_DIR = /opt/render/project/src/.agents
   ```

5. **Add Database:**
   - Scroll to bottom → "Add Database" or
   - Separately: New + → PostgreSQL
   - Name: `agent-management-db`
   - Plan: Free
   - Link to your web service (DATABASE_URL auto-added)

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 2-3 minutes
   - ⚠️ **SAVE YOUR URL!** (e.g., https://agent-management-api.onrender.com)

### Step 3: Verify Backend
```bash
# Replace with your URL
curl https://your-backend.onrender.com/health
# Should return: {"status":"healthy","version":"1.0.0"}

curl https://your-backend.onrender.com/api/stats
# Should return stats

# Sync your 16 agents
curl -X POST https://your-backend.onrender.com/api/agents/sync
```

---

## 🎨 FRONTEND DEPLOYMENT (Vercel)

### Method 1: CLI (Fastest - 2 minutes)

```bash
cd /home/rpas/wildfire-simulator-v2/agent-management-platform/frontend

# Set your backend URL (from Render)
export BACKEND_URL="https://your-backend.onrender.com"
echo "VITE_API_URL=$BACKEND_URL" > .env.production

# Install dependencies
npm install

# Deploy to Vercel
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (Select your account)
# - Link to existing project? No
# - What's your project's name? agent-management-platform
# - In which directory is your code located? ./
# - Want to override settings? No

# ⚠️ SAVE YOUR FRONTEND URL!
```

### Method 2: Vercel Dashboard (Alternative)

1. **Go to:** https://vercel.com
2. **Import Project:**
   - Click "Add New..." → "Project"
   - Import: `Tphambolio/wildfire-simulator-v2`

3. **Configure:**
   ```
   Framework Preset:    Vite
   Root Directory:      agent-management-platform/frontend
   Build Command:       npm run build
   Output Directory:    dist
   Install Command:     npm install
   ```

4. **Environment Variables:**
   Add this before deploying:
   ```
   VITE_API_URL = https://your-backend.onrender.com
   ```

5. **Deploy!**
   - Click "Deploy"
   - Wait 1-2 minutes
   - ⚠️ **SAVE YOUR URL!**

---

## 🧪 TESTING YOUR DEPLOYMENT

### Test Backend
```bash
# Health check
curl https://your-backend.onrender.com/health

# List agents
curl https://your-backend.onrender.com/api/agents

# API documentation
open https://your-backend.onrender.com/docs
```

### Test Frontend
1. Open: https://your-frontend.vercel.app
2. Should see dashboard (might take a moment to load)
3. Check browser console for errors
4. Try navigating the interface

### Full Integration Test
```bash
# Create a test project
curl -X POST https://your-backend.onrender.com/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"test-project","description":"Testing deployment"}'

# Assign a task
curl -X POST https://your-backend.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name":"performance-agent",
    "project_id":"test-project",
    "title":"Test deployment",
    "description":"Verify the platform works",
    "priority":1
  }'

# View in dashboard
# Go to your frontend URL and check tasks
```

---

## 📝 POST-DEPLOYMENT CHECKLIST

- [ ] Backend URL saved and accessible
- [ ] Frontend URL saved and accessible
- [ ] Backend health check passes
- [ ] 16 agents synced (check /api/agents)
- [ ] Frontend loads without errors
- [ ] Can create a project via API
- [ ] Can assign a task via API
- [ ] Dashboard displays data correctly

---

## 🎉 DEPLOYMENT COMPLETE!

**Your URLs:**
- 🌐 Dashboard: `https://________.vercel.app`
- 🔌 Backend API: `https://________.onrender.com`
- 📚 API Docs: `https://________.onrender.com/docs`

**Share these URLs:**
- With your team
- In your documentation
- Anywhere you want agent management!

---

## 🔧 Common Issues

**Backend:**
- "Application failed to respond" → Check logs in Render dashboard
- Database errors → Verify DATABASE_URL is set
- Agents not showing → Run curl -X POST .../api/agents/sync

**Frontend:**
- Can't connect to backend → Check VITE_API_URL in Vercel env vars
- CORS errors → Backend should allow all origins (check app.main:CORS_ORIGINS)
- Build fails → Check Node version (should use npm install, not yarn)

**Both:**
- First deploy is slow (2-3 min) → Be patient!
- Free tier sleeps after inactivity → First request wakes it up (~30 sec)

---

## 📊 Monitoring

**Render:**
- Dashboard → Service → Logs (live tail)
- Dashboard → Service → Metrics
- Email alerts for failures

**Vercel:**
- Dashboard → Project → Deployments
- Dashboard → Project → Analytics
- Runtime logs for each deployment

---

**Need help? Check logs first, then review this checklist! 🚀**
