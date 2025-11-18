# 🚀 Agent Management Platform - Quick Start

## What You Have Built

✅ **MCP Server** - Working! 16 agents synced
✅ **FastAPI Backend** - Full REST API with WebSocket  
✅ **React Frontend** - Dashboard UI (Vite + React)
✅ **Database** - SQLite (dev) / PostgreSQL (prod)
✅ **Deployment Ready** - Docker + Cloud configs

## 1️⃣ Start Using MCP Server NOW

The MCP server is **ready to use** with Claude Code immediately!

### Setup (One-Time)

```bash
cd /home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server

# Add to Claude Code config
mkdir -p ~/.config/claude
cat >> ~/.config/claude/mcp_config.json << 'EOF'
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
EOF
```

### Use in Claude Code

Restart Claude Code, then use these tools:

```
list_agents
→ Shows all 16 agents

assign_task 
  agent_name="performance-agent"
  project_id="wildfire-simulator"
  title="Optimize FBP calculations"
  description="Review performance bottlenecks"
  priority=3

get_report report_id="..."

list_tasks project_id="wildfire-simulator"
```

## 2️⃣ Deploy Web Dashboard to Cloud

### Option A: One-Click Deploy (Fastest)

**Backend (Render.com):**
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect GitHub: `Tphambolio/wildfire-simulator-v2`
4. Settings:
   - **Root Dir**: `agent-management-platform/backend`
   - **Build**: `pip install -r requirements.txt`
   - **Start**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database (auto-connects)
6. Deploy! ✨

**Frontend (Vercel):**
```bash
cd agent-management-platform/frontend
npm install
npx vercel --prod
```

Set environment variable in Vercel:
- `VITE_API_URL`: `https://your-backend.onrender.com`

### Option B: Docker (Local Testing)

```bash
cd agent-management-platform

# Start backend
cd backend
docker build -t agent-mgmt-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./agent_management.db \
  -e AGENTS_DIR=/app/.agents \
  -v /home/rpas/wildfire-simulator-v2/.agents:/app/.agents \
  agent-mgmt-backend

# Start frontend
cd ../frontend
npm install
npm run dev
```

Visit: http://localhost:5173

## 3️⃣ Test Backend Locally

```bash
cd agent-management-platform/backend

# Install dependencies
pip install -r requirements.txt

# Run server
python3 -m uvicorn app.main:app --reload

# Test
curl http://localhost:8000/health
curl http://localhost:8000/api/agents
curl http://localhost:8000/docs  # Swagger UI
```

## 📊 Your Agent Workforce

**16 Agents Ready:**
- visualization-agent
- monte-carlo-agent
- spatial-analysis-agent
- spotting-model-agent
- performance-tuning-agent
- fbp-algorithm-agent
- scientific-validation-agent
- weather-data-agent
- security-agent
- testing-agent
- code-quality-agent
- performance-agent
- backend-cleanup-agent
- refactoring-agent
- documentation-agent
- frontend-cleanup-agent

## 🎯 Next Steps

1. **Use MCP Now**: Start assigning tasks via Claude Code
2. **Deploy Dashboard**: Get it online in 10 minutes
3. **Test Workflows**: Assign tasks, view reports
4. **Scale**: Add more agents, projects, integrations

## 📚 Full Guides

- Deployment: See `DEPLOYMENT_GUIDE.md`
- MCP Server: See `mcp-server/README.md`
- API Docs: http://localhost:8000/docs (when running)

## 🆘 Quick Fixes

**MCP not showing tools?**
- Restart Claude Code
- Check `~/.config/claude/mcp_config.json`
- Test: `python3 -m agent_mcp_server.cli status`

**Backend won't start?**
- Check Python version: `python3 --version` (needs 3.10+)
- Install deps: `pip install -r requirements.txt`
- Check logs: `tail -f /tmp/backend.log`

**Frontend not connecting?**
- Check `VITE_API_URL` in `.env.local`
- Verify backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors

---

**🎉 You're ready to manage your AI workforce!**
