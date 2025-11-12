# MCP Server Integration Guide

## Overview
This guide explains how to set up Model Context Protocol (MCP) servers for enhanced multi-agent coordination in the Wildfire Simulator project.

## What is MCP?

MCP (Model Context Protocol) enables Claude instances to:
- Share filesystem access across sessions
- Maintain shared memory/context between agents
- Coordinate work through shared state
- Enable true parallel execution with context sharing

## Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
bash setup-wildfire-simulator-agents.sh
```

This will:
1. Check for Node.js and npm
2. Install MCP servers globally
3. Configure Claude Desktop automatically
4. Verify installation

### Option 2: Manual Setup

#### Step 1: Install Node.js and npm
```bash
# Ubuntu/Debian/Mint
sudo apt update
sudo apt install nodejs npm

# Verify installation
node --version  # Should be v14+ or higher
npm --version
```

#### Step 2: Install MCP Servers
```bash
# Install filesystem MCP server
npm install -g @modelcontextprotocol/server-filesystem

# Install memory MCP server
npm install -g @modelcontextprotocol/server-memory

# Verify installation
npx @modelcontextprotocol/server-filesystem --help
npx @modelcontextprotocol/server-memory --help
```

#### Step 3: Configure Claude Desktop

**Location**: `~/.config/Claude/claude_desktop_config.json`

**If file doesn't exist**, create it:
```bash
mkdir -p ~/.config/Claude
cp .claude/mcp_config.json ~/.config/Claude/claude_desktop_config.json
```

**If file exists**, merge the MCP configuration:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/home/rpas/wildfire-simulator-v2"
      ]
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    }
  }
}
```

**Important**: Replace `/home/rpas/wildfire-simulator-v2` with your actual project path.

#### Step 4: Restart Claude Desktop
After editing the configuration:
1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. MCP servers should auto-connect

## Verification

### Check MCP Server Status
In Claude Desktop or Claude Code, you should see:
- MCP icon/indicator showing connected servers
- Filesystem access to project directory
- Memory server available for context sharing

### Test Filesystem Access
```bash
# In Claude, try:
# "List files in the .agents directory using MCP filesystem"
```

### Test Memory Access
```bash
# In Claude, try:
# "Store this in MCP memory: project_name = wildfire-simulator-v2"
# "Retrieve project_name from MCP memory"
```

## How Agents Use MCP

### Filesystem MCP
- **Read agent prompts**: Agents can directly read `.agents/domain_agents/*.txt`
- **Read task files**: Access `.agents/domain_agents/tasks/*.json`
- **Write reports**: Output to `.agents/domain_agents/reports/*.json`
- **Update status**: Modify `.agents/domain_agents/status/*.json`

### Memory MCP
- **Share context**: Agents store findings in shared memory
- **Coordinate work**: Agents check what others have discovered
- **Avoid duplication**: Agents see what's already been done
- **Knowledge base**: Accumulate learnings across sessions

## Example Agent Workflow with MCP

### Traditional (File-Based Only)
```
Agent A: Read task → Work → Write report → Done
Agent B: Read task → Work → Write report → Done
(No communication between agents)
```

### Enhanced (With MCP)
```
Agent A: Read task → Store "working on FBP audit" in MCP memory → Work → Write report → Store findings in MCP
Agent B: Read task → Check MCP memory → See Agent A working on FBP → Coordinate on different task → Work → Store findings in MCP
Agent C: Read task → Check MCP memory → See findings from A & B → Build on their work → Complete
```

## MCP Memory Keys

### Recommended Naming Convention
```
wildfire:[category]:[key]

Examples:
- wildfire:fbp:audit_complete
- wildfire:fwi:validation_status
- wildfire:monte_carlo:sample_count
- wildfire:performance:bottlenecks_found
```

### Agent Communication via Memory
```javascript
// Agent A stores finding
await memory.set("wildfire:fbp:extreme_bui_issue", {
  "agent": "fbp-algorithm-agent",
  "finding": "BUI > 150 causes ROS suppression",
  "recommendation": "Implement extreme BUI correction",
  "priority": "critical"
});

// Agent B retrieves finding
const finding = await memory.get("wildfire:fbp:extreme_bui_issue");
// Agent B can now address this finding
```

## Troubleshooting

### MCP Servers Not Connecting

**Check Node.js/npm**:
```bash
which node
which npm
node --version
npm --version
```

**Check MCP packages**:
```bash
npm list -g @modelcontextprotocol/server-filesystem
npm list -g @modelcontextprotocol/server-memory
```

**Re-install if needed**:
```bash
npm uninstall -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-filesystem
```

### Configuration File Issues

**Check file exists**:
```bash
ls -la ~/.config/Claude/claude_desktop_config.json
```

**Validate JSON**:
```bash
cat ~/.config/Claude/claude_desktop_config.json | python3 -m json.tool
```

**Check permissions**:
```bash
chmod 644 ~/.config/Claude/claude_desktop_config.json
```

### Filesystem Access Denied

**Check project path** in config is correct:
```bash
pwd  # In project directory
# Should match path in claude_desktop_config.json
```

**Check permissions**:
```bash
ls -ld /home/rpas/wildfire-simulator-v2
# Should be readable by your user
```

## Benefits of MCP Integration

### For Single Agents
- Direct filesystem access (faster reads/writes)
- Persistent memory across sessions
- Better context management

### For Multi-Agent Coordination
- **Shared context**: All agents see same memory
- **Avoid conflicts**: Agents coordinate via memory locks
- **Knowledge sharing**: Findings immediately available to all
- **True parallelism**: Multiple agents work simultaneously with shared state

### For Development Workflow
- **Faster iteration**: Agents remember previous sessions
- **Better coordination**: PM can orchestrate via shared memory
- **Real-time monitoring**: Monitor agents via memory queries
- **Reproducibility**: MCP logs all interactions

## Advanced Usage

### Agent-to-Agent Messages
```javascript
// Agent A sends message
await memory.set("messages:for_weather_agent", {
  "from": "fbp-algorithm-agent",
  "message": "Need validation of ISI calculation at high wind speeds",
  "priority": "high",
  "timestamp": new Date().toISOString()
});

// Weather Agent checks messages
const messages = await memory.get("messages:for_weather_agent");
```

### Shared Task Queue
```javascript
// PM creates task queue
await memory.set("task_queue", [
  {"task": "audit_fbp", "assigned_to": "fbp-algorithm-agent", "status": "in_progress"},
  {"task": "validate_fwi", "assigned_to": "weather-data-agent", "status": "pending"},
  {"task": "optimize_monte_carlo", "assigned_to": "performance-tuning-agent", "status": "pending"}
]);

// Agents update their status
const queue = await memory.get("task_queue");
queue[0].status = "completed";
await memory.set("task_queue", queue);
```

### Knowledge Base
```javascript
// Accumulate findings
const kb = await memory.get("knowledge_base") || {};
kb.extreme_bui_correction = {
  "agent": "fbp-algorithm-agent",
  "discovery": "BUI effect equation suppresses ROS at BUI > 150",
  "solution": "Apply extreme multiplier: 1 + (BUI - 150) / 50",
  "validated": true,
  "timestamp": "2025-10-28T14:00:00Z"
};
await memory.set("knowledge_base", kb);
```

## Without MCP (Current State)

The system works fine without MCP using file-based coordination:
- Agents read from task files
- Agents write to status/report files
- PM aggregates reports manually
- Sequential execution

## With MCP (Enhanced)

Added capabilities:
- Real-time agent communication
- True parallel execution with shared state
- Faster file operations
- Better context persistence
- Advanced coordination patterns

## Conclusion

MCP integration is **optional but recommended** for:
- Large multi-agent workflows
- Parallel agent execution
- Advanced coordination needs
- Better performance

The system functions perfectly well without MCP using traditional file-based coordination. MCP adds sophistication and efficiency for power users.

---

**Setup Status**: Run `bash setup-wildfire-simulator-agents.sh` to auto-configure
**Support**: See troubleshooting section above or check agent logs
**Documentation**: https://modelcontextprotocol.io/docs
