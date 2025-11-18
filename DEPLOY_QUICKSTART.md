# 🚀 Quick Deploy - Get Online in 10 Minutes

The fastest way to get your Agent Management Platform online!

## Option A: Railway (Recommended - Easiest)

### Step 1: Deploy Backend (5 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd agent-management-platform/backend
railway init
railway up

# Set environment variables in Railway dashboard:
# - DEBUG=false
# - CORS_ORIGINS=https://your-frontend.vercel.app
```

**Get your backend URL**: Check Railway dashboard → Settings → Domains

### Step 2: Deploy Frontend (3 minutes)

```bash
# Create .env.production with your backend URL
cd ../frontend
echo "VITE_API_URL=https://your-backend.railway.app" > .env.production

# Deploy to Vercel
npm install -g vercel
vercel --prod
```

**Done!** Your app is live 🎉

---

## Option B: One-Click Deploy

### Vercel (Frontend Only)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Tphambolio/wildfire-simulator-v2&project-name=agent-management&root-directory=agent-management-platform/frontend)

**Note**: You'll still need to deploy the backend separately (Railway recommended)

---

## Option C: Docker on Your Server (15 minutes)

If you have a VPS (DigitalOcean, AWS, etc.):

```bash
# 1. SSH to your server
ssh user@your-server-ip

# 2. Clone repo
git clone https://github.com/Tphambolio/wildfire-simulator-v2.git
cd wildfire-simulator-v2/agent-management-platform

# 3. Copy your agents
scp -r .agents user@your-server-ip:~/wildfire-simulator-v2/

# 4. Run with Docker
docker-compose up -d --build

# Access at: http://your-server-ip
```

---

## Post-Deployment Checklist

After deploying:

- [ ] Visit your app URL and verify it loads
- [ ] Check `/api/health` endpoint
- [ ] Test agent discovery
- [ ] Create a test task
- [ ] (Optional) Set ANTHROPIC_API_KEY for real LLM execution

---

## Quick Commands

### Check Backend Status
```bash
curl https://your-backend-url.com/health
```

### View API Docs
Visit: `https://your-backend-url.com/docs`

### Update Environment Variables

**Railway:**
```bash
railway variables set ANTHROPIC_API_KEY=sk-your-key
```

**Vercel:**
```bash
vercel env add VITE_API_URL production
```

---

## Cost Breakdown

| Option | Monthly Cost | Setup Time |
|--------|-------------|------------|
| Railway + Vercel | $5-10 | 10 mins |
| Render Free Tier | $0 (limited) | 15 mins |
| Docker VPS | $5-20 | 20 mins |

**Recommended**: Railway + Vercel for best balance of ease and cost.

---

## Troubleshooting

### "API connection refused"
- Check frontend VITE_API_URL matches backend URL
- Verify CORS_ORIGINS includes frontend URL

### "Agents not found"
- Make sure .agents directory exists
- Check AGENT_ROOT_DIR environment variable

### "Module not found"
- Verify MCP server is installed in build process
- Check build logs for errors

---

## Need Help?

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions
2. Visit Railway/Vercel docs
3. Open an issue on GitHub

Ready to deploy? Pick an option above and go! 🚀
