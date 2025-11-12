# Agent Management Platform - Deployment Guide

## 🚀 Quick Deployment to Cloud

### Backend Deployment (Render.com)

1. **Push to GitHub** (if not already done):
```bash
cd /home/rpas/wildfire-simulator-v2
git add agent-management-platform/
git commit -m "Add Agent Management Platform"
git push origin dashboard-focused
```

2. **Deploy to Render**:
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `Tphambolio/wildfire-simulator-v2`
   - Configure:
     - **Name**: `agent-management-api`
     - **Root Directory**: `agent-management-platform/backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       - `PYTHON_VERSION`: `3.10.0`
       - `DATABASE_URL`: (Render will provide PostgreSQL)
       - `AGENTS_DIR`: `/opt/render/project/src/.agents`

3. **Add PostgreSQL Database**:
   - In Render dashboard, go to "New +" → "PostgreSQL"
   - Name it `agent-management-db`
   - Connect it to your web service
   - Render will auto-inject `DATABASE_URL`

### Frontend Deployment (Vercel)

1. **Deploy to Vercel**:
```bash
cd agent-management-platform/frontend
npm install
npm run build

# Deploy
npx vercel --prod
```

2. **Configure Environment Variables** in Vercel:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add:
     - `VITE_API_URL`: `https://agent-management-api.onrender.com` (your Render backend URL)

3. **Alternative: Deploy via GitHub**:
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Set Root Directory to `agent-management-platform/frontend`
   - Vercel will auto-detect Vite and deploy

## 🏃 Local Development

### Backend

```bash
cd agent-management-platform/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./agent_management.db
AGENTS_DIR=/home/rpas/wildfire-simulator-v2/.agents
PORT=8000
EOF

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be at: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend

```bash
cd agent-management-platform/frontend

# Install dependencies
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

Frontend will be at: http://localhost:5173

## 📊 Using the Platform

### Via Web Dashboard

1. **Open Frontend**: https://your-app.vercel.app
2. **View Agents**: See all 16 agents with status
3. **Create Task**: Click "New Task" and assign to an agent
4. **View Reports**: Check agent outputs and reports
5. **Monitor**: Real-time updates via WebSocket

### Via MCP (Claude Code)

1. **Configure MCP** in `~/.config/claude/mcp_config.json`:
```json
{
  "mcpServers": {
    "agent-management": {
      "command": "python3",
      "args": ["-m", "agent_mcp_server.server"],
      "env": {
        "PYTHONPATH": "/home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server",
        "DATABASE_URL": "sqlite:////home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server/agent_management.db",
        "AGENTS_DIR": "/home/rpas/wildfire-simulator-v2/.agents"
      }
    }
  }
}
```

2. **Use in Claude Code**:
```
list_agents
assign_task agent_name="fbp-algorithm-agent" title="Review FBP calculations" ...
get_report report_id="..."
```

### Via REST API

```bash
# Get all agents
curl https://agent-management-api.onrender.com/api/agents

# Create task
curl -X POST https://agent-management-api.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "performance-agent",
    "project_id": "wildfire-simulator",
    "title": "Optimize performance",
    "description": "Review and optimize critical paths",
    "priority": 3
  }'

# Get stats
curl https://agent-management-api.onrender.com/api/stats
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
cd agent-management-platform

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/agent_management
      - AGENTS_DIR=/app/.agents
    volumes:
      - ../../.agents:/app/.agents
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=agent_management
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# Run
docker-compose up -d
```

## 🔧 Troubleshooting

### Backend Issues

**Database connection errors**:
```bash
# Check DATABASE_URL is set correctly
echo $DATABASE_URL

# For PostgreSQL, format should be:
# postgresql://user:password@host:port/database
```

**Agents not found**:
```bash
# Verify AGENTS_DIR path
ls -la /home/rpas/wildfire-simulator-v2/.agents

# Sync agents manually
curl -X POST http://localhost:8000/api/agents/sync
```

### Frontend Issues

**API connection errors**:
- Check `VITE_API_URL` environment variable
- Verify backend is running and accessible
- Check CORS settings in backend

**Build errors**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📈 Monitoring

### Health Checks

```bash
# Backend health
curl https://agent-management-api.onrender.com/health

# Check stats
curl https://agent-management-api.onrender.com/api/stats
```

### Logs

**Render**:
- Go to your service dashboard
- Click "Logs" tab
- Real-time log streaming

**Vercel**:
- Go to your project
- Click "Deployments"
- Select deployment → "Runtime Logs"

## 🎯 Next Steps

1. **Security**: Add authentication/authorization
2. **Scaling**: Configure auto-scaling in Render
3. **Monitoring**: Add Sentry or similar for error tracking
4. **Analytics**: Add usage analytics
5. **Webhooks**: Add webhook notifications for task completion

## 📚 API Documentation

Once deployed, visit:
- **Swagger UI**: https://agent-management-api.onrender.com/docs
- **ReDoc**: https://agent-management-api.onrender.com/redoc

## 🤝 Support

- Check logs first
- Review environment variables
- Test API endpoints directly
- Verify database connectivity

---

**Your platform is ready to deploy! 🚀**

Backend API: Full REST API with WebSocket
Frontend: React dashboard with real-time updates  
MCP Server: Claude Code integration
Database: PostgreSQL (production) / SQLite (dev)
Agents: 16 agents synced and ready
