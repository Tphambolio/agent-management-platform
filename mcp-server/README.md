# Agent Management Platform MCP Server

MCP Server that exposes your agent workforce via the Model Context Protocol.

## Features

- 🤖 **Agent Management**: List, register, and monitor agents
- 📋 **Task Assignment**: Assign tasks to agents via MCP tools
- 📊 **Report Retrieval**: Get beautiful, formatted reports
- 🔄 **Real-time Status**: Monitor agent activity and task progress
- 🎯 **Project Support**: Manage multiple projects with the same agent team

## Installation

\`\`\`bash
cd /home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server
pip install -e .
\`\`\`

## Setup with Claude Code

Add to \`~/.config/claude/mcp_config.json\`:

\`\`\`json
{
  "mcpServers": {
    "agent-management": {
      "command": "python",
      "args": ["-m", "agent_mcp_server.server"],
      "env": {
        "DATABASE_URL": "sqlite:////home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server/agent_management.db",
        "AGENTS_DIR": "/home/rpas/wildfire-simulator-v2/.agents"
      }
    }
  }
}
\`\`\`

## Available MCP Tools

- \`list_agents\` - List all registered agents
- \`get_agent\` - Get agent details
- \`assign_task\` - Assign task to agent
- \`get_task_status\` - Check task status
- \`get_report\` - Retrieve reports
- \`list_projects\` - List projects
- \`create_project\` - Create new project

## Quick Start

\`\`\`bash
# Install
pip install -e .

# Initialize database and sync agents
python -m agent_mcp_server.cli init
python -m agent_mcp_server.cli sync

# Start server (for testing)
python -m agent_mcp_server.server
\`\`\`

Then use in Claude Code!
