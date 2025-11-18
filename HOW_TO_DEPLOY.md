# 🌐 How to Put Your Agent Management Platform Online

**You have 4 easy options to choose from!**

---

## 🏆 OPTION 1: Railway + Vercel (EASIEST - RECOMMENDED)

**Time:** 10 minutes | **Cost:** ~$5-10/month | **Difficulty:** ⭐ Easy

This is the fastest way and works great for most users.

### Step-by-Step:

#### Deploy Backend to Railway:

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login and Deploy**:
   ```bash
   cd agent-management-platform/backend
   railway login
   railway init
   railway up
   ```

3. **Set Environment Variables** in Railway Dashboard (https://railway.app/dashboard):
   - Click your project → Variables
   - Add:
     ```
     DEBUG=false
     CORS_ORIGINS=https://your-frontend.vercel.app
     ```

4. **Get Your Backend URL**:
   - Go to Settings → Networking → Generate Domain
   - Copy the URL (e.g., `https://agent-backend-production.up.railway.app`)

#### Deploy Frontend to Vercel:

1. **Create .env.production**:
   ```bash
   cd agent-management-platform/frontend
   echo "VITE_API_URL=https://YOUR-BACKEND-URL.railway.app" > .env.production
   ```
   ⚠️ Replace `YOUR-BACKEND-URL` with your actual Railway URL!

2. **Deploy**:
   ```bash
   npm install -g vercel
   vercel --prod
   ```

3. **Update CORS in Railway**:
   - Go back to Railway dashboard
   - Update `CORS_ORIGINS` to include your Vercel URL

✅ **Done!** Your app is live at your Vercel URL!

**Access:**
- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-backend.railway.app`
- API Docs: `https://your-backend.railway.app/docs`

---

## 🐳 OPTION 2: Docker on Your Own Server

**Time:** 20 minutes | **Cost:** $5-20/month (VPS) | **Difficulty:** ⭐⭐ Medium

Perfect if you want full control and have a server (DigitalOcean, AWS, Linode, etc.)

### Step-by-Step:

1. **Get a VPS** (if you don't have one):
   - [DigitalOcean](https://www.digitalocean.com) - $6/month droplet works great
   - [Linode](https://www.linode.com) - $5/month
   - Any Ubuntu 22.04 server with 1GB RAM

2. **SSH to your server**:
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo apt install docker-compose-plugin
   ```

4. **Clone your repository**:
   ```bash
   git clone https://github.com/Tphambolio/wildfire-simulator-v2.git
   cd wildfire-simulator-v2/agent-management-platform
   ```

5. **Copy your agents** (from your local machine):
   ```bash
   # On your local machine:
   scp -r /path/to/wildfire-simulator-v2/.agents root@your-server-ip:~/wildfire-simulator-v2/
   ```

6. **Update docker-compose.yml** with your server IP:
   ```bash
   nano docker-compose.yml
   # Update CORS_ORIGINS to include http://your-server-ip
   ```

7. **Build and run**:
   ```bash
   docker-compose up -d --build
   ```

8. **Check it's running**:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

✅ **Done!** Access your app:
- Frontend: `http://your-server-ip`
- Backend: `http://your-server-ip:8000`
- API Docs: `http://your-server-ip:8000/docs`

**Optional - Add HTTPS** (recommended):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 🎯 OPTION 3: Render.com (Free Tier Available)

**Time:** 15 minutes | **Cost:** FREE (limited) or $7-25/month | **Difficulty:** ⭐⭐ Medium

Good free option with automatic HTTPS.

### Step-by-Step:

1. **Sign up** at [render.com](https://render.com)

2. **Deploy Backend**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - **Root Directory**: Leave blank
     - **Build Command**:
       ```
       cd agent-management-platform/mcp-server && pip install -e . && cd ../backend && pip install -r requirements.txt
       ```
     - **Start Command**:
       ```
       cd agent-management-platform/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
       ```
   - Add Environment Variables:
     ```
     PYTHON_VERSION=3.11.0
     DEBUG=false
     ```

3. **Deploy Frontend**:
   - Click "New +" → "Static Site"
   - Settings:
     - **Root Directory**: `agent-management-platform/frontend`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `dist`
   - Add Environment Variable:
     ```
     VITE_API_URL=https://your-backend.onrender.com
     ```

4. **Update Backend CORS**:
   - Go to backend service → Environment
   - Add:
     ```
     CORS_ORIGINS=https://your-frontend.onrender.com
     ```

✅ **Done!** Both services will auto-deploy when you push to GitHub!

---

## ⚡ OPTION 4: One-Line Deploy Script

**Time:** 5 minutes | **Cost:** $5-10/month | **Difficulty:** ⭐ Very Easy

Use the automated script I created:

```bash
cd agent-management-platform
./deploy-railway.sh
```

This script will:
- Install Railway CLI if needed
- Deploy backend to Railway
- Configure environment variables
- Give you the backend URL
- Set up frontend configuration

Then just deploy frontend:
```bash
cd frontend
vercel --prod
```

✅ **Done!**

---

## 📊 Comparison Table

| Option | Time | Monthly Cost | Difficulty | Best For |
|--------|------|--------------|------------|----------|
| **Railway + Vercel** | 10 min | $5-10 | ⭐ Easy | Most users |
| **Docker VPS** | 20 min | $5-20 | ⭐⭐ Medium | Full control |
| **Render Free** | 15 min | $0 | ⭐⭐ Medium | Testing |
| **Deploy Script** | 5 min | $5-10 | ⭐ Very Easy | Quick start |

---

## ✅ After Deployment Checklist

Once deployed, verify everything works:

1. **Check Backend Health**:
   ```bash
   curl https://your-backend-url.com/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Visit API Docs**:
   Open: `https://your-backend-url.com/docs`

3. **Test Frontend**:
   - Visit your frontend URL
   - Should see the dashboard
   - Check that agents are listed

4. **Test Creating a Task**:
   - Click "Tasks" → "Create Task"
   - Assign to an agent
   - Verify it works

5. **Check Real-Time Updates**:
   - Dashboard should refresh every 5-10 seconds
   - Agent status should update

---

## 🔒 Security - IMPORTANT!

Before going live, do this:

1. **Change SECRET_KEY** in backend environment:
   ```
   SECRET_KEY=generate-a-random-50-character-string-here
   ```
   Generate one: https://randomkeygen.com/

2. **Set DEBUG=false** (already in configs above)

3. **Configure CORS properly** - only include your actual domains

4. **Use HTTPS** - Railway/Vercel do this automatically

5. **(Optional) Add ANTHROPIC_API_KEY** for real LLM execution:
   ```
   ANTHROPIC_API_KEY=sk-your-actual-key
   ```

---

## 🆘 Troubleshooting

### "API connection refused" in browser:
- Check frontend VITE_API_URL is correct
- Verify backend CORS_ORIGINS includes frontend URL
- Make sure backend is running

### "No agents found":
- On Railway: agents must be in the repo or uploaded manually
- On Docker: make sure you copied the .agents directory
- Check logs: `railway logs` or `docker-compose logs`

### "Module not found" during build:
- Make sure MCP server is installed first in build command
- Check build logs for the exact error
- Verify Python version is 3.10+

### Frontend shows "Loading..." forever:
- Check browser console for errors
- Verify API URL is correct
- Test backend health endpoint directly

---

## 💡 Pro Tips

1. **Start with Railway + Vercel** - easiest to set up and maintain

2. **Use the free tier first** - test everything before paying

3. **Monitor your usage** - all platforms have dashboards showing costs

4. **Set up uptime monitoring**:
   - [UptimeRobot](https://uptimerobot.com) - free
   - [Pingdom](https://www.pingdom.com) - paid

5. **Enable auto-deploy** - push to GitHub → auto-deploy to production

---

## 🎉 You're Ready!

Pick whichever option fits you best and follow the steps. You'll be online in 10-20 minutes!

**Need help?** Check:
- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive guide
- [DEPLOY_QUICKSTART.md](DEPLOY_QUICKSTART.md) - Quick reference
- GitHub Issues

**My recommendation:** Start with Option 1 (Railway + Vercel). It's the easiest and most reliable!
