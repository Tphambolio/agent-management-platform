# Deploy to Railway - Step-by-Step Guide

## Prerequisites
- Node.js installed (you have this)
- Your agent-management-platform code
- A Railway account (free to create)

---

## Step 1: Install Railway CLI

```bash
# Install Railway CLI globally
npm install -g @railway/cli

# Verify installation
railway --version
```

Expected output: `railway version x.x.x`

---

## Step 2: Login to Railway

```bash
# This will open your browser to authenticate
railway login
```

- Browser will open
- Click "Login" or "Sign Up" (use GitHub for easiest signup)
- Grant permissions
- Return to terminal

Expected output: `🎉 Logged in as your-email@example.com`

---

## Step 3: Deploy Backend

```bash
# Navigate to backend directory
cd /home/user/wildfire-simulator-v2/agent-management-platform/backend

# Initialize Railway project
railway init

# Choose:
# - "Create new project" → Yes
# - Project name → "agent-management-backend" (or your choice)
# - Environment → "production"

# Deploy the backend
railway up
```

**What happens:**
- Railway uploads your code
- Detects it's a Python project
- Installs dependencies from requirements.txt
- Starts your FastAPI server
- Assigns a public URL

Expected output:
```
✓ Deployment live at https://agent-management-backend-production-xxxx.up.railway.app
```

---

## Step 4: Configure Backend Environment Variables

```bash
# Set environment variables
railway variables set DEBUG=false
railway variables set HOST=0.0.0.0
railway variables set PORT='$PORT'

# (Optional) Add your Anthropic API key for real LLM execution
railway variables set ANTHROPIC_API_KEY=sk-your-key-here
```

---

## Step 5: Get Your Backend URL

```bash
# Generate a public domain
railway domain

# This will show your backend URL like:
# https://agent-management-backend-production-xxxx.up.railway.app
```

**Copy this URL** - you'll need it for the frontend!

---

## Step 6: Test Backend

```bash
# Replace with your actual backend URL
curl https://your-backend-url.up.railway.app/health

# Should return:
# {"status":"healthy","agents_discovered":X,"tasks_total":X,...}
```

Visit in browser: `https://your-backend-url.up.railway.app/docs`

You should see the Swagger API documentation!

---

## Step 7: Configure Frontend

```bash
# Navigate to frontend directory
cd /home/user/wildfire-simulator-v2/agent-management-platform/frontend

# Create production environment file
echo "VITE_API_URL=https://your-backend-url.up.railway.app" > .env.production
```

⚠️ **Replace `your-backend-url.up.railway.app` with your actual Railway backend URL!**

---

## Step 8: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

**What happens:**
- Vercel asks for project settings
- Choose "yes" for all defaults
- Builds your React app
- Deploys to a public URL

Expected output:
```
✓ Production: https://your-app-xxxx.vercel.app
```

---

## Step 9: Update Backend CORS

```bash
# Go back to backend directory
cd ../backend

# Update CORS with your frontend URL
railway variables set CORS_ORIGINS=https://your-app-xxxx.vercel.app

# Railway will automatically redeploy with new settings
```

---

## Step 10: Verify Everything Works

### Test Backend
```bash
curl https://your-backend-url.up.railway.app/health
curl https://your-backend-url.up.railway.app/api/agents
```

### Test Frontend
Open in browser: `https://your-app.vercel.app`

You should see:
- ✅ Dashboard loads
- ✅ Agents are listed
- ✅ No CORS errors in browser console

---

## 🎉 You're Live!

Your Agent Management Platform is now online:

- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-backend-url.up.railway.app`
- **API Docs**: `https://your-backend-url.up.railway.app/docs`

---

## Useful Railway Commands

```bash
# View logs
railway logs

# Check deployment status
railway status

# Open project in browser
railway open

# List environment variables
railway variables

# Link to different project
railway link

# Redeploy
railway up --detach

# Delete project
railway delete
```

---

## Troubleshooting

### "railway: command not found"
```bash
# Make sure npm global bin is in PATH
npm config get prefix
# Add this to ~/.bashrc: export PATH="$(npm config get prefix)/bin:$PATH"
source ~/.bashrc
railway --version
```

### "Build failed: Module not found"
```bash
# Make sure you're in the backend directory
cd /home/user/wildfire-simulator-v2/agent-management-platform/backend
railway up
```

### "Port already in use"
Railway automatically sets `$PORT` - make sure your config uses it:
```bash
railway variables set PORT='$PORT'
```

### "No agents found"
The agents are discovered from the `.agents` directory. You have two options:

**Option A: Include agents in deployment** (if they're in your git repo)
```bash
# Make sure .agents is committed
git add ../../.agents
git commit -m "add agents"
git push
railway up
```

**Option B: Mount agents directory** (Railway Volumes - paid feature)
Or just use mock execution for testing.

### CORS errors
```bash
# Make sure CORS_ORIGINS includes your frontend URL
railway variables set CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

---

## Cost

**Railway Pricing:**
- Free tier: $5 credit/month
- After free tier: ~$5-10/month for basic usage
- Pay only for what you use

**Vercel Pricing:**
- Free tier: Very generous
- Hobby plan: Free for most use cases
- Pro: $20/month (only if you need it)

**Total estimated cost: $5-10/month**

---

## Updating Your Deployment

### Update Backend
```bash
cd /home/user/wildfire-simulator-v2/agent-management-platform/backend
# Make your changes...
railway up
```

### Update Frontend
```bash
cd /home/user/wildfire-simulator-v2/agent-management-platform/frontend
# Make your changes...
vercel --prod
```

---

## Optional: Set Up Auto-Deploy

### For Backend (Railway)
```bash
# Connect to GitHub
railway link
# Then enable GitHub integration in Railway dashboard
# Every git push will auto-deploy!
```

### For Frontend (Vercel)
Vercel automatically sets up GitHub integration:
- Every push to your branch auto-deploys
- Pull requests get preview deployments

---

## Next Steps

1. ✅ Share your app URL with your team
2. ✅ Test creating tasks and viewing reports
3. ✅ (Optional) Add custom domain
4. ✅ Set up monitoring (Railway has built-in metrics)
5. ✅ Enable auto-deploy from GitHub

---

## Support

- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs
- Railway Discord: https://discord.gg/railway
