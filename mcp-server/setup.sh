#!/bin/bash
# Setup script for Agent Management Platform MCP Server

set -e

echo "════════════════════════════════════════════════════════════"
echo "  Agent Management Platform MCP Server Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MCP_SERVER_DIR="/home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server"
CLAUDE_CONFIG_DIR="$HOME/.config/claude"
CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/mcp_config.json"

# Step 1: Install dependencies
echo -e "${BLUE}[1/5]${NC} Installing Python dependencies..."
cd "$MCP_SERVER_DIR"
pip install -e . -q
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Step 2: Initialize database
echo -e "${BLUE}[2/5]${NC} Initializing database..."
python -m agent_mcp_server.cli init
echo -e "${GREEN}✓${NC} Database initialized"
echo ""

# Step 3: Sync agents
echo -e "${BLUE}[3/5]${NC} Syncing agents from filesystem..."
python -m agent_mcp_server.cli sync
echo ""

# Step 4: Create default project
echo -e "${BLUE}[4/5]${NC} Creating default project..."
python -m agent_mcp_server.cli create-project "wildfire-simulator" \
    --description "Wildfire Simulator V2" \
    --repo-path "/home/rpas/wildfire-simulator-v2" 2>/dev/null || echo "  (Project may already exist)"
echo -e "${GREEN}✓${NC} Default project configured"
echo ""

# Step 5: Configure Claude Code MCP
echo -e "${BLUE}[5/5]${NC} Configuring Claude Code MCP integration..."

mkdir -p "$CLAUDE_CONFIG_DIR"

# Check if config file exists
if [ ! -f "$CLAUDE_CONFIG" ]; then
    echo "{}" > "$CLAUDE_CONFIG"
fi

# Backup existing config
cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup-$(date +%Y%m%d-%H%M%S)"

# Update MCP config
python3 << 'PYTHON_EOF'
import json
import os

config_file = os.path.expanduser("~/.config/claude/mcp_config.json")

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
except:
    config = {}

if "mcpServers" not in config:
    config["mcpServers"] = {}

config["mcpServers"]["agent-management"] = {
    "command": "python",
    "args": ["-m", "agent_mcp_server.server"],
    "env": {
        "DATABASE_URL": "sqlite:////home/rpas/wildfire-simulator-v2/agent-management-platform/mcp-server/agent_management.db",
        "AGENTS_DIR": "/home/rpas/wildfire-simulator-v2/.agents"
    }
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✓ Updated {config_file}")
PYTHON_EOF

echo -e "${GREEN}✓${NC} Claude Code MCP configured"
echo ""

# Show status
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}Setup Complete!${NC}"
echo "════════════════════════════════════════════════════════════"
echo ""
python -m agent_mcp_server.cli status
echo ""
echo "════════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "────────────────────────────────────────────────────────────"
echo "1. Restart Claude Code to load the new MCP server"
echo "2. Try: ${YELLOW}list_agents${NC} in Claude Code"
echo "3. Try: ${YELLOW}assign_task${NC} to give work to an agent"
echo ""
echo "For more info: cat $MCP_SERVER_DIR/README.md"
echo "════════════════════════════════════════════════════════════"
