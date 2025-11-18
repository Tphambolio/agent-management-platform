# Agent Management Platform - Quick Start Guide

## Installation

1. **Run the installation script:**
   ```bash
   cd agent-management-platform/mcp-server
   ./install.sh
   ```

2. **Configure (optional):**
   ```bash
   # Edit .env and add your Anthropic API key for LLM-powered execution
   nano .env
   ```
   If you don't add an API key, the system will use mock execution (still fully functional for testing).

## Testing the MCP Server

### Option 1: Test Locally with Python

```bash
# Activate virtual environment
source venv/bin/activate

# Run the server
python -m agent_mcp
```

The server will start and wait for MCP protocol messages on stdin/stdout.

### Option 2: Integrate with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "agent-management": {
      "command": "python",
      "args": ["-m", "agent_mcp"],
      "cwd": "/full/path/to/wildfire-simulator-v2/agent-management-platform/mcp-server/src",
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Restart Claude Desktop, and you'll see the agent management tools available!

### Option 3: Use with Claude Code (MCP Client)

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json

async def test_agent_platform():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "agent_mcp"],
        cwd="/path/to/agent-management-platform/mcp-server/src"
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List all agents
            print("📋 Listing agents...")
            result = await session.call_tool("list_agents", {})
            agents = json.loads(result.content[0].text)
            print(json.dumps(agents, indent=2))

            # Get specific agent
            if agents["agents"]:
                agent_id = agents["agents"][0]["id"]
                print(f"\n🔍 Getting details for agent: {agent_id}")
                result = await session.call_tool("get_agent_status", {"agent_id": agent_id})
                print(json.loads(result.content[0].text))

asyncio.run(test_agent_platform())
```

## Example Workflows

### 1. List Your Agents

```
You: List all my agents

Claude (via MCP): [Uses list_agents tool]
Found 15 agents:
- code-review-agent (development)
- performance-agent (development)
- fbp-algorithm-agent (domain)
- security-agent (development)
...
```

### 2. Assign a Task

```
You: Assign a code review task to the code-review-agent for the authentication module

Claude (via MCP):
[Uses assign_task tool]
Task created successfully!
- Task ID: abc123
- Agent: code-review-agent
- Title: Review authentication module
- Status: pending

[Uses execute_task tool]
Task is now running...
```

### 3. Check Task Status

```
You: What's the status of task abc123?

Claude (via MCP):
[Uses get_task_status tool]
Task Status:
- Status: completed
- Started: 2025-11-07 10:30:00
- Completed: 2025-11-07 10:32:15
- Result: Successfully analyzed authentication code
```

### 4. Get the Report

```
You: Show me the report for that task

Claude (via MCP):
[Uses list_reports + get_report tools]

Report: Review authentication module
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
The authentication module follows security best practices...

Findings:
✓ Password hashing uses bcrypt
✓ Session management properly implemented
⚠ Consider adding rate limiting to prevent brute force

Recommendations:
1. Add rate limiting middleware
2. Implement 2FA support
3. Add security headers
```

### 5. Create a Project

```
You: Create a new project called "E-commerce Platform"

Claude (via MCP):
[Uses create_project tool]
Project created!
- ID: proj-456
- Name: E-commerce Platform
- Ready for agent assignments
```

### 6. Assign Multiple Agents to a Project

```
You: Assign performance analysis and security review to the E-commerce Platform project

Claude (via MCP):
[Uses assign_task twice with project_id]

Created 2 tasks for E-commerce Platform:
1. Performance Analysis (performance-agent) - pending
2. Security Review (security-agent) - pending

Ready to execute!
```

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_agents` | List all available agents |
| `get_agent_status` | Get detailed agent information |
| `assign_task` | Create and assign a task to an agent |
| `execute_task` | Start executing a pending task |
| `get_task_status` | Check task progress and results |
| `list_tasks` | List all tasks with filters |
| `get_report` | Retrieve an agent-generated report |
| `list_reports` | List all reports |
| `create_project` | Create a new project |
| `list_projects` | List all projects |
| `get_project` | Get project details |

## Troubleshooting

### "Agent not found"
- Make sure your agents are defined in `.agents/domain_agents/` or `.agents/development_team/`
- Check that agent files end in `.txt`
- Run `list_agents` to see what was discovered

### "ANTHROPIC_API_KEY not set"
- This is fine! The system will use mock execution
- Mock execution is fully functional for testing
- Add the API key to `.env` if you want real LLM-powered execution

### "Task failed"
- Check the task error with `get_task_status`
- Verify the agent file exists and is readable
- Check logs for detailed error information

## Next Steps

Now that your MCP server is running, you can:

1. **Use it via Claude Desktop** - Just talk naturally and Claude will use the tools
2. **Build integrations** - Any MCP client can connect to your agent workforce
3. **Add more agents** - Drop new agent definitions in `.agents/` and they'll be discovered
4. **Extend functionality** - Add custom tools, prompts, or execution methods

Want to add a web dashboard? Continue to the next phase where we'll build a FastAPI backend and React frontend on top of this MCP foundation!
