# Getting Started with Agent Management Platform

Welcome! This guide will get you up and running in under 5 minutes.

## What You're Building

A professional platform to manage your AI agent workforce with three ways to interact:

1. **Claude Desktop** - Talk to your agents naturally via MCP
2. **Web Dashboard** - Beautiful visual interface at http://localhost:3000
3. **REST API** - Programmatic access for integrations

## Step-by-Step Setup

### Step 1: Install the MCP Server (Core Component)

```bash
cd agent-management-platform/mcp-server
./install.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Set up configuration files
- Create necessary directories

### Step 2: Test Your Installation

```bash
venv/bin/python test_server.py
```

You should see:
```
🚀 Testing Agent Management Platform MCP Server
✓ Agent manager initialized
✓ Found X agents
✓ Task created
✓ Task completed successfully
✅ MCP Server Test Complete!
```

**Congratulations!** Your MCP server is working. You can now use it with Claude Desktop.

### Step 3: Configure Claude Desktop (Optional but Recommended)

Add this to your Claude Desktop config file:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-management": {
      "command": "python",
      "args": ["-m", "agent_mcp"],
      "cwd": "/FULL/PATH/TO/wildfire-simulator-v2/agent-management-platform/mcp-server/src",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here-optional"
      }
    }
  }
}
```

Replace `/FULL/PATH/TO/` with your actual path. Find it by running:
```bash
cd agent-management-platform/mcp-server/src && pwd
```

Restart Claude Desktop and you're ready to go!

### Step 4: Try It Out in Claude Desktop

Open Claude Desktop and try:

```
List all my agents
```

Claude will use the MCP tool to show your agent workforce!

```
Assign a performance analysis task to the performance-agent
```

Claude will create and execute the task for you!

---

## Want the Web Dashboard Too?

### Step 5: Start the Backend API

Open a new terminal:

```bash
cd agent-management-platform/backend
./run.sh
```

The API will start at http://localhost:8000

Visit http://localhost:8000/docs to see the interactive API documentation!

### Step 6: Start the Frontend

Open another terminal:

```bash
cd agent-management-platform/frontend
npm install  # First time only
npm run dev
```

The dashboard will open at http://localhost:3000

## 🎉 You're Done!

You now have:
- ✅ MCP server running (works with Claude Desktop)
- ✅ REST API at http://localhost:8000
- ✅ Web dashboard at http://localhost:3000

## Next Steps

### Use Claude Desktop
Just talk naturally:
- "What agents do I have?"
- "Create a security review task"
- "Show me recent reports"

### Use the Web Dashboard
- View all agents and their status
- Create and assign tasks
- Monitor execution in real-time
- Read beautiful formatted reports
- Organize work by projects

### Use the API
```bash
# List agents
curl http://localhost:8000/api/agents

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "your-agent-id",
    "title": "Task title",
    "description": "What to do",
    "priority": "high"
  }'
```

## Troubleshooting

### "No agents found"
- Make sure you have agent definition files in `.agents/domain_agents/` or `.agents/development_team/`
- Agent files should be `.txt` files
- Run the rediscover endpoint: `curl -X POST http://localhost:8000/api/agents/rediscover`

### "Port already in use"
- Backend: Change `PORT` in `backend/.env`
- Frontend: Change port in `frontend/vite.config.js`

### "ANTHROPIC_API_KEY not set"
- This is optional! The system works with mock execution
- Add your API key to `mcp-server/.env` if you want real LLM-powered agent execution

### "Module not found"
- Make sure you activated the virtual environment:
  ```bash
  source venv/bin/activate  # Mac/Linux
  venv\Scripts\activate     # Windows
  ```

## Configuration

### Enable Real LLM Execution

Edit `mcp-server/.env`:
```env
ANTHROPIC_API_KEY=sk-your-actual-api-key
```

Agents will now use Claude to process tasks instead of mock execution!

### Change API Port

Edit `backend/.env`:
```env
PORT=8080
```

### Add CORS Origins

Edit `backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://myapp.com
```

## Advanced Usage

### Create a Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "E-commerce Platform",
    "description": "Customer project",
    "repository_path": "/path/to/repo"
  }'
```

### Assign Multiple Agents to a Project

Create tasks with the same `project_id` to group them together.

### Monitor with WebSockets

Connect to `ws://localhost:8000/api/ws/updates` for real-time updates.

## Architecture at a Glance

```
Claude Desktop (MCP) ──┐
Web Dashboard ─────────┼──> Backend API ──> MCP Server ──> Your Agents
REST API Clients ──────┘
```

## Resources

- **Full Documentation**: See `README.md`
- **MCP Quick Start**: See `mcp-server/QUICKSTART.md`
- **Design Docs**: See `.agents/AGENT_MANAGEMENT_PLATFORM_DESIGN.md`
- **API Docs**: Visit http://localhost:8000/docs when backend is running

## Support

Having issues? Check:
1. All services are running (MCP server, backend, frontend)
2. Ports are not blocked
3. Virtual environments are activated
4. Agent definition files exist in `.agents/`

## What's Next?

- Add more agents to your workforce
- Create projects for different clients
- Build custom integrations with the REST API
- Extend the MCP server with custom tools
- Customize the frontend dashboard

**Happy agent managing!** 🚀
