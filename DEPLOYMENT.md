# Deployment Guide - Agent Management Platform

Get your Agent Management Platform online and accessible from anywhere!

## 🚀 Deployment Options

### Option 1: Railway.app (Easiest - Recommended)
**Perfect for:** Quick deployment, free tier available, automatic HTTPS

#### Deploy Backend:

1. **Sign up** at [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy Backend**:
   ```bash
   cd agent-management-platform/backend
   railway init
   railway up
   ```

4. **Set Environment Variables** in Railway dashboard:
   ```
   HOST=0.0.0.0
   PORT=$PORT
   DEBUG=false
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ANTHROPIC_API_KEY=sk-your-key (optional)
   ```

5. **Get your backend URL**: `https://agent-management-backend-production.up.railway.app`

#### Deploy Frontend:

1. **Update API URL** in `frontend/vite.config.js`:
   ```javascript
   export default defineConfig({
     plugins: [react()],
     server: {
       proxy: {
         '/api': {
           target: 'https://your-backend-url.railway.app',
           changeOrigin: true,
         },
       },
     },
   })
   ```

2. **Deploy to Vercel**:
   ```bash
   cd agent-management-platform/frontend
   npm install -g vercel
   vercel
   ```

3. **Done!** Your app is live at `https://your-app.vercel.app`

---

### Option 2: Render.com (Also Easy)
**Perfect for:** Full-stack deployment, free tier, databases included

#### Steps:

1. **Sign up** at [render.com](https://render.com)

2. **Create New Web Service**:
   - Connect your GitHub repository
   - Select `agent-management-platform/backend` as root directory
   - Build Command: `pip install -r ../mcp-server/requirements.txt && cd ../mcp-server && pip install -e . && cd ../backend && pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**:
   ```
   PYTHON_VERSION=3.11.0
   DEBUG=false
   CORS_ORIGINS=https://your-frontend.onrender.com
   ```

4. **Deploy Frontend**:
   - Create New Static Site
   - Root Directory: `agent-management-platform/frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`

5. **Update frontend API URL** to point to your backend URL

---

### Option 3: Docker + VPS (Most Control)
**Perfect for:** Self-hosting, full control, any VPS provider

#### Prerequisites:
- VPS (DigitalOcean, Linode, AWS EC2, etc.)
- Docker and Docker Compose installed
- Domain name (optional)

#### Steps:

1. **SSH into your VPS**:
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo apt-get install docker-compose-plugin
   ```

3. **Clone your repository**:
   ```bash
   git clone https://github.com/Tphambolio/wildfire-simulator-v2.git
   cd wildfire-simulator-v2/agent-management-platform
   ```

4. **Copy your agent definitions**:
   ```bash
   # Copy your .agents directory to the server
   scp -r .agents user@your-server-ip:~/wildfire-simulator-v2/
   ```

5. **Configure environment**:
   ```bash
   # Update backend/.env and frontend/vite.config.js with your server's IP or domain
   ```

6. **Build and run**:
   ```bash
   docker-compose up -d --build
   ```

7. **Access your app**:
   - Frontend: `http://your-server-ip`
   - Backend: `http://your-server-ip:8000`
   - API Docs: `http://your-server-ip:8000/docs`

#### Setup HTTPS (Recommended):

1. **Install Certbot**:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Get SSL Certificate**:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

---

### Option 4: DigitalOcean App Platform (Balanced)
**Perfect for:** Easy deployment with more control than Heroku

#### Steps:

1. **Sign up** at [digitalocean.com](https://www.digitalocean.com)

2. **Create New App**:
   - Connect GitHub repository
   - Select `agent-management-platform`

3. **Configure Backend Service**:
   - Type: Web Service
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - HTTP Port: 8080

4. **Configure Frontend Service**:
   - Type: Static Site
   - Build Command: `cd frontend && npm install && npm run build`
   - Output Directory: `frontend/dist`

5. **Add Environment Variables** in the dashboard

6. **Deploy!**

---

## 🔧 Configuration for Production

### Backend Environment Variables:
```env
HOST=0.0.0.0
PORT=8000  # or $PORT for cloud platforms
DEBUG=false
SECRET_KEY=generate-a-secure-random-key-here
CORS_ORIGINS=https://your-frontend-url.com,https://www.your-frontend-url.com
ANTHROPIC_API_KEY=sk-your-key-if-you-want-real-llm-execution
```

### Frontend Build Configuration:

Update `frontend/vite.config.js` for production:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
})
```

Add `.env.production` in frontend:
```env
VITE_API_URL=https://your-backend-url.com
```

---

## 📊 Recommended Setup (Best Value)

**For most users, I recommend:**

1. **Backend on Railway.app**
   - Free tier: $5/month credit
   - Easy deployment
   - Automatic HTTPS
   - Cost: ~$5-10/month for basic usage

2. **Frontend on Vercel**
   - Free tier is generous
   - Excellent performance
   - Built-in CDN
   - Cost: Free for most use cases

3. **Total Cost: ~$5-10/month**

---

## 🔐 Security Checklist

Before going live:

- [ ] Change `SECRET_KEY` in backend/.env to a secure random string
- [ ] Set `DEBUG=false` in production
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set up environment variables securely
- [ ] Don't commit `.env` files to git
- [ ] Consider adding authentication for sensitive data

---

## 🧪 Test Your Deployment

After deployment:

1. **Check Backend Health**:
   ```bash
   curl https://your-backend-url.com/health
   ```

2. **Check API Docs**:
   Visit `https://your-backend-url.com/docs`

3. **Test Frontend**:
   Visit `https://your-frontend-url.com`

4. **Check Agent Discovery**:
   ```bash
   curl https://your-backend-url.com/api/agents
   ```

---

## 🎯 Quick Deploy Script

Want to deploy to Railway in one command?

```bash
#!/bin/bash
# deploy.sh - Quick deploy to Railway

echo "🚀 Deploying Agent Management Platform..."

# Backend
cd agent-management-platform/backend
railway init
railway up
BACKEND_URL=$(railway domain)

echo "✅ Backend deployed: $BACKEND_URL"

# Update frontend config
cd ../frontend
echo "VITE_API_URL=https://$BACKEND_URL" > .env.production

# Deploy frontend to Vercel
vercel --prod

echo "✅ Deployment complete!"
```

---

## 🆘 Troubleshooting

### "Module not found" errors
- Make sure MCP server is installed in the build process
- Check build commands include `cd mcp-server && pip install -e .`

### CORS errors in browser
- Add your frontend URL to `CORS_ORIGINS` in backend env vars
- Include both `https://` and `http://` versions

### Agent discovery fails
- Make sure `.agents` directory is copied to the server
- Check file permissions
- Verify AGENT_ROOT_DIR environment variable

### API connection refused
- Check backend URL in frontend config
- Verify backend is running and accessible
- Check firewall rules on VPS

---

## 📞 Next Steps After Deployment

1. **Share the URL** with your team
2. **Monitor usage** in platform dashboards
3. **Set up monitoring** (optional):
   - [UptimeRobot](https://uptimerobot.com) for uptime monitoring
   - [Sentry](https://sentry.io) for error tracking
4. **Scale as needed** - Most platforms auto-scale

---

## 💰 Cost Estimates

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Railway | $5 credit/month | $5-20/month | Backend |
| Vercel | Generous free | $20/month | Frontend |
| Render | 750 hrs/month | $7-25/month | Full-stack |
| DigitalOcean | None | $5-50/month | VPS control |
| Docker VPS | None | $5-20/month | Full control |

**Recommended: Railway (backend) + Vercel (frontend) = ~$5-10/month**

---

Need help? Check the troubleshooting section or open an issue on GitHub!
