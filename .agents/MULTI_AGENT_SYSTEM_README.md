# Wildfire Simulator Multi-Agent System
## Complete Guide to the Enhanced Agent Ecosystem

**Version**: 2.0
**Last Updated**: 2025-10-28
**Status**: ✅ Fully Operational

---

## 🎯 Quick Start

### 1. One-Command Setup
```bash
bash setup-wildfire-simulator-agents.sh
```

### 2. Run Your First Agent
```bash
# Single agent
bash .agents/development_team/run-agent.sh fbp-algorithm-agent

# Multiple agents in parallel
bash run-agents-parallel.sh fbp-algorithm-agent weather-data-agent
```

### 3. Monitor Live
```bash
bash monitor-agents.sh
```

That's it! You're running a sophisticated multi-agent system.

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Agent Types](#agent-types)
3. [Getting Started](#getting-started)
4. [Running Agents](#running-agents)
5. [Monitoring & Reports](#monitoring--reports)
6. [Agent Coordination](#agent-coordination)
7. [DNA Evolution System](#dna-evolution-system)
8. [MCP Integration](#mcp-integration)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## System Overview

### What is This?

A **multi-agent AI system** specifically designed for wildfire simulation development, featuring:

- **25+ specialized AI agents** working together
- **8 domain-specific** wildfire experts (NEW!)
- **4 development team** agents for code quality
- **5 coordination agents** for project management
- **12+ core system agents** for various tasks

### Why Multi-Agent?

**Traditional Development**:
- One developer does everything
- Sequential tasks
- Knowledge siloed

**Multi-Agent Development**:
- Specialists focus on expertise areas
- Parallel execution (3-5x faster)
- Accumulated knowledge shared
- Continuous learning via DNA system

### Key Features

✅ **Parallel Execution**: Run multiple agents simultaneously
✅ **Domain Expertise**: 8 wildfire science specialists
✅ **DNA Evolution**: Agents learn and improve over time
✅ **Live Monitoring**: Real-time dashboard
✅ **MCP Integration**: Optional enhanced coordination
✅ **Automated Setup**: One command to configure everything

---

## Agent Types

### 🔬 Domain Specialists (NEW!)

**8 wildfire science experts**:

1. **FBP-Algorithm-Agent**: Canadian FBP system expert
2. **Weather-Data-Agent**: FWI calculations and weather processing
3. **Spatial-Analysis-Agent**: GIS operations and raster processing
4. **Performance-Tuning-Agent**: Code optimization (Numba, vectorization)
5. **Spotting-Model-Agent**: Ember transport and spotting fires
6. **Monte-Carlo-Agent**: Stochastic simulation and statistics
7. **Scientific-Validation-Agent**: Benchmark validation and accuracy
8. **Visualization-Agent**: Maps, animations, dashboards

**When to use**: Technical work on fire behavior, weather, performance, validation

### 🛠️ Development Team

**4 code quality agents**:

1. **Backend-Cleanup-Agent**: Python linting, type hints, refactoring
2. **Frontend-Cleanup-Agent**: HTML/CSS/JS optimization
3. **Refactoring-Agent**: Architecture improvements
4. **Documentation-Agent**: Docstrings, READMEs, guides

**When to use**: Code cleanup, refactoring, documentation

### 🎯 Coordination Agents

**5 project management agents**:

1. **PM-Orchestrator**: Task planning and coordination
2. **Security-Agent**: Vulnerability scanning
3. **Testing-Agent**: QA and test coverage
4. **Performance-Agent**: General performance analysis
5. **Code-Quality-Agent**: Standards enforcement

**When to use**: Project planning, security audits, testing

### 🔧 Core System Agents

**12+ specialized system agents** (existing):
- Fire Model Agent, Dataset Agent, Validation Agent, etc.

**When to use**: System-level operations

---

## Getting Started

### Prerequisites

**Required**:
- Linux (tested on Ubuntu/Mint)
- Python 3.8+
- Bash shell
- Git

**Optional (for MCP)**:
- Node.js 14+
- npm

**Python Packages**:
```bash
pip install numpy rasterio geopandas numba matplotlib
```

### Installation

#### Step 1: Navigate to Project
```bash
cd ~/wildfire-simulator-v2
```

#### Step 2: Run Setup
```bash
bash setup-wildfire-simulator-agents.sh
```

This will:
- ✅ Verify directory structure
- ✅ Check Python environment
- ✅ Install MCP servers (if Node.js available)
- ✅ Configure Claude Desktop
- ✅ Create necessary directories
- ✅ Verify existing agents
- ✅ Run health check

#### Step 3: Verify Installation
```bash
bash .agents/health-check.sh
```

Expected output:
```
=== Wildfire Simulator Agent System Health Check ===

Directory Structure:
  ✓ .agents
  ✓ .agents/development_team
  ✓ .agents/domain_agents
  ✓ .agents/dna

Agent Prompts:
  Found: 17 agent prompt files

DNA Genomes:
  Found: 4 genome files

...

Health check complete!
```

---

## Running Agents

### Method 1: Single Agent

**Syntax**:
```bash
bash .agents/development_team/run-agent.sh <agent-name>
```

**Examples**:
```bash
# Run FBP algorithm specialist
bash .agents/development_team/run-agent.sh fbp-algorithm-agent

# Run weather data specialist
bash .agents/development_team/run-agent.sh weather-data-agent

# Run PM orchestrator
bash .agents/development_team/run-agent.sh pm-orchestrator
```

**What happens**:
1. Script reads agent prompt from `.agents/domain_agents/[agent].txt`
2. Executes agent with Claude Code CLI
3. Agent reads tasks from `.agents/domain_agents/tasks/[agent]-tasks.json`
4. Agent works through tasks
5. Agent writes status to `.agents/domain_agents/status/[agent]-status.json`
6. Agent generates report in `.agents/domain_agents/reports/[agent]-report.json`

### Method 2: Multiple Agents (Parallel)

**Syntax**:
```bash
bash run-agents-parallel.sh <agent1> <agent2> <agent3> ...
```

**Examples**:
```bash
# Run 3 domain specialists in parallel
bash run-agents-parallel.sh fbp-algorithm-agent weather-data-agent spatial-analysis-agent

# Run all development team agents
bash run-agents-parallel.sh backend-cleanup-agent frontend-cleanup-agent refactoring-agent documentation-agent

# Mix domain and development agents
bash run-agents-parallel.sh fbp-algorithm-agent backend-cleanup-agent performance-tuning-agent
```

**Benefits**:
- ⚡ **3-5x faster** than sequential execution
- 📊 **Aggregate reporting** automatically
- 🔄 **Parallel progress** tracking
- 📋 **Single execution log** for all agents

**What happens**:
1. Launches each agent as background process
2. Monitors all agents simultaneously
3. Updates status files in real-time
4. Waits for all to complete
5. Generates aggregate report
6. Shows summary statistics

### Method 3: Interactive Menu

**For development team agents**:
```bash
bash .agents/dev-team-controller.sh
```

**Interactive menu** lets you:
- Select agents to run
- View agent status
- Check reports
- Run health checks

---

## Monitoring & Reports

### Live Monitoring Dashboard

**Start monitor**:
```bash
bash monitor-agents.sh
```

**Dashboard shows**:
```
╔════════════════════════════════════════════════════════════════╗
║              Wildfire Simulator Multi-Agent Monitor            ║
╠════════════════════════════════════════════════════════════════╣
║ 2025-10-28 14:30:00                Auto-refresh: 2s           ║
╚════════════════════════════════════════════════════════════════╝

━━━ Domain Specialist Agents ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agent                          Status      Progress              Last Update
────────────────────────────────────────────────────────────────────────────
fbp-algorithm-agent            RUNNING     [████████░░░░] 75%    2s ago
weather-data-agent             COMPLETE    [████████████] 100%   5m ago
spatial-analysis-agent         RUNNING     [█████░░░░░░░] 40%    1s ago
performance-tuning-agent       PENDING     [░░░░░░░░░░░░]  0%    -
...

━━━ Summary ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Agents: 17  │  RUNNING: 2  │  COMPLETE: 8  │  FAILED: 0  │  IDLE: 7
```

**Features**:
- 🔄 Auto-refreshes every 2 seconds
- 📊 Progress bars for each agent
- ⏰ Time since last update
- 🎨 Color-coded status
- 📈 Summary statistics

**Exit**: Press `Ctrl+C`

### Manual Status Check

**Check specific agent**:
```bash
cat .agents/domain_agents/status/fbp-algorithm-agent-status.json | python3 -m json.tool
```

**Output**:
```json
{
  "agent": "fbp-algorithm-agent",
  "status": "completed",
  "start_time": "2025-10-28T14:00:00Z",
  "end_time": "2025-10-28T14:15:00Z",
  "execution_id": "20251028_140000",
  "exit_code": 0,
  "progress": 100,
  "tasks_completed": 5,
  "log_file": ".agents/logs/domain_agents/fbp-algorithm-agent.log"
}
```

### View Reports

**Agent report**:
```bash
cat .agents/domain_agents/reports/fbp-algorithm-agent-report.json | python3 -m json.tool
```

**Aggregate report (parallel execution)**:
```bash
cat .agents/development_team/reports/parallel_execution_20251028_140000.json | python3 -m json.tool
```

### View Logs

**Individual agent log**:
```bash
tail -f .agents/logs/domain_agents/fbp-algorithm-agent.log
```

**Parallel execution logs**:
```bash
tail -f .agents/logs/parallel/*
```

---

## Agent Coordination

### Task Files

**Location**: `.agents/domain_agents/tasks/[agent]-tasks.json`

**Format**:
```json
{
  "agent": "fbp-algorithm-agent",
  "version": "1.0",
  "tasks": [
    {
      "task_id": "fbp-001",
      "priority": "critical",
      "status": "pending",
      "objective": "Audit extreme BUI handling",
      "scope": {
        "files": ["src/core/fbp_calculator.py"]
      },
      "success_criteria": [
        "BUI effect equation verified",
        "Test cases created for BUI 150-200"
      ]
    }
  ]
}
```

**Modify tasks**:
```bash
nano .agents/domain_agents/tasks/fbp-algorithm-agent-tasks.json
```

### Status Files

**Location**: `.agents/domain_agents/status/[agent]-status.json`

**Auto-updated** by agents during execution

**States**: `pending`, `running`, `completed`, `failed`, `blocked`

### Report Files

**Location**: `.agents/domain_agents/reports/[agent]-report.json`

**Generated** by agents after task completion

**Contains**: Findings, changes made, validation results, recommendations

### Coordination Protocol

**How agents coordinate**:

1. **Read tasks** from task file
2. **Update status** to "running"
3. **Check DNA** for previous learnings
4. **Execute work** systematically
5. **Update progress** in status file
6. **Generate report** with findings
7. **Update DNA** with new patterns
8. **Set status** to "completed"

**PM Orchestrator coordinates**:
1. Assesses project needs
2. Creates tasks for specialists
3. Monitors agent status
4. Resolves blockers
5. Aggregates reports
6. Presents summary to human PM

---

## DNA Evolution System

### What is DNA?

**Agent DNA** = Persistent learning across sessions

**Components**:
- **Skills**: Technical abilities acquired
- **Patterns**: Reusable solutions discovered
- **Techniques**: Specific methods mastered
- **Pitfalls**: Mistakes to avoid
- **Insights**: High-level wisdom

### DNA Structure

**Location**: `.agents/domain_agents/dna/[agent]/`

```
fbp-algorithm-agent/
├── genome.json                # Complete DNA record
├── experience/
│   ├── patterns/              # Reusable patterns
│   ├── techniques/            # Specific techniques
│   └── solutions/             # Problem solutions
├── skills/                    # Skill documentation
└── memory/                    # Session context
```

### How DNA Works

**Session 1** (No DNA):
- Agent starts as novice
- Learns FBP systems
- Documents patterns
- Saves DNA at end

**Session 2** (With DNA):
- Agent loads DNA (instant expert!)
- Recalls 11 skills
- Applies 12 patterns
- Avoids 10 pitfalls
- Builds on previous work

**Result**: Exponential learning curve

### View DNA

**Check agent genome**:
```bash
cat .agents/domain_agents/dna/fbp-algorithm-agent/genome.json | python3 -m json.tool
```

**Evolution summary**:
```bash
cat .agents/AGENT_DNA_SUMMARY.md
```

### Evolution Scripts

**Manual evolution**:
```bash
bash .agents/evolve.sh
```

**Scientific evolution**:
```bash
bash .agents/evolve_scientific.sh
```

---

## MCP Integration

### What is MCP?

**Model Context Protocol** = Enhanced agent coordination

**Enables**:
- Shared filesystem access
- Shared memory between agents
- Real-time coordination
- Faster file operations

### Setup MCP

**Automated**:
```bash
bash setup-wildfire-simulator-agents.sh
```

**Manual**:
See `.agents/MCP_INTEGRATION_GUIDE.md`

### Is MCP Required?

**NO** - System works perfectly without MCP

**Without MCP**: File-based coordination (works great)
**With MCP**: Enhanced speed and coordination (nice to have)

**Recommendation**: Start without MCP, add later if needed

---

## Troubleshooting

### Agent Won't Run

**Check**: Agent prompt file exists
```bash
ls -la .agents/domain_agents/fbp-algorithm-agent.txt
```

**Check**: Task file is valid JSON
```bash
cat .agents/domain_agents/tasks/fbp-algorithm-agent-tasks.json | python3 -m json.tool
```

**Check**: Claude Code CLI available
```bash
which claude
claude --version
```

### Tasks Not Completing

**Check status file**:
```bash
cat .agents/domain_agents/status/fbp-algorithm-agent-status.json
```

**Look for**: "blocked" status or error messages

**Check log file**:
```bash
tail -100 .agents/logs/domain_agents/fbp-algorithm-agent.log
```

### Parallel Execution Fails

**Check**: No conflicting file access
```bash
# Ensure agents work on different files
```

**Check**: Enough system resources
```bash
htop  # Monitor CPU/memory usage
```

**Reduce parallelism**: Run fewer agents at once

### Reports Not Generated

**Check**: Agent completed successfully
```bash
cat .agents/domain_agents/status/fbp-algorithm-agent-status.json | grep status
```

**Check**: Reports directory exists
```bash
ls -la .agents/domain_agents/reports/
```

**Check**: Permissions
```bash
ls -la .agents/domain_agents/
```

---

## Advanced Usage

### Custom Agent Creation

**1. Create prompt file**:
```bash
nano .agents/domain_agents/my-custom-agent.txt
```

**2. Create task file**:
```bash
nano .agents/domain_agents/tasks/my-custom-agent-tasks.json
```

**3. Run agent**:
```bash
bash run-agents-parallel.sh my-custom-agent
```

### Agent Collaboration Patterns

**Sequential**: Agent B waits for Agent A
```bash
bash .agents/development_team/run-agent.sh agent-a
bash .agents/development_team/run-agent.sh agent-b  # Runs after A
```

**Parallel**: Agents work simultaneously
```bash
bash run-agents-parallel.sh agent-a agent-b agent-c
```

**Hierarchical**: PM orchestrates specialists
```bash
# 1. PM creates tasks
bash .agents/development_team/run-agent.sh pm-orchestrator

# 2. Review PM report
cat .agents/development_team/reports/PM_DASHBOARD.md

# 3. Run specialists in parallel
bash run-agents-parallel.sh fbp-algorithm-agent weather-data-agent spatial-analysis-agent
```

### Performance Optimization

**Profile agents**:
```bash
time bash run-agents-parallel.sh agent-a agent-b
```

**Monitor resources**:
```bash
# In another terminal
htop
```

**Adjust parallelism**:
```bash
# Run fewer agents if system is slow
bash run-agents-parallel.sh agent-a agent-b  # Instead of 5 agents
```

---

## Quick Reference

### File Locations

```
wildfire-simulator-v2/
├── setup-wildfire-simulator-agents.sh   # Setup script
├── run-agents-parallel.sh               # Parallel runner
├── monitor-agents.sh                    # Live monitor
├── .agents/
│   ├── domain_agents/                   # Domain specialists
│   │   ├── [agent].txt                  # Agent prompts
│   │   ├── tasks/[agent]-tasks.json     # Task definitions
│   │   ├── status/[agent]-status.json   # Current status
│   │   ├── reports/[agent]-report.json  # Agent reports
│   │   └── dna/[agent]/                 # Learning DNA
│   ├── development_team/                # Dev team agents
│   ├── ENHANCED_AGENT_REGISTRY.md       # Complete agent list
│   ├── MCP_INTEGRATION_GUIDE.md         # MCP setup guide
│   └── MULTI_AGENT_ENHANCEMENT_PROPOSAL.md  # Enhancement details
└── .claude/
    └── mcp_config.json                  # MCP configuration
```

### Common Commands

```bash
# Setup
bash setup-wildfire-simulator-agents.sh

# Run single agent
bash .agents/development_team/run-agent.sh <agent-name>

# Run multiple agents
bash run-agents-parallel.sh <agent1> <agent2> ...

# Monitor live
bash monitor-agents.sh

# Health check
bash .agents/health-check.sh

# View status
cat .agents/domain_agents/status/<agent>-status.json | python3 -m json.tool

# View report
cat .agents/domain_agents/reports/<agent>-report.json | python3 -m json.tool

# View log
tail -f .agents/logs/domain_agents/<agent>.log
```

### Agent Names Reference

**Domain Specialists**:
- `fbp-algorithm-agent`
- `weather-data-agent`
- `spatial-analysis-agent`
- `performance-tuning-agent`
- `spotting-model-agent`
- `monte-carlo-agent`
- `scientific-validation-agent`
- `visualization-agent`

**Development Team**:
- `backend-cleanup-agent`
- `frontend-cleanup-agent`
- `refactoring-agent`
- `documentation-agent`

**Coordination**:
- `pm-orchestrator`
- `security-agent`
- `testing-agent`
- `performance-agent`
- `code-quality-agent`

---

## Support

### Documentation

- **This guide**: `.agents/MULTI_AGENT_SYSTEM_README.md`
- **Agent registry**: `.agents/ENHANCED_AGENT_REGISTRY.md`
- **Enhancement proposal**: `.agents/MULTI_AGENT_ENHANCEMENT_PROPOSAL.md`
- **MCP guide**: `.agents/MCP_INTEGRATION_GUIDE.md`
- **DNA system**: `.agents/AGENT_DNA_SUMMARY.md`
- **Architecture**: `.agents/ARCHITECTURE.md`

### Getting Help

1. **Check logs**: `.agents/logs/`
2. **Review status files**: `.agents/domain_agents/status/`
3. **Run health check**: `bash .agents/health-check.sh`
4. **Check documentation** listed above

### Reporting Issues

Include:
- Agent name
- Command executed
- Error message
- Status file contents
- Log file excerpt

---

## Summary

You now have a **world-class multi-agent system** for wildfire simulation development!

**Key Capabilities**:
- ✅ 25+ specialized agents
- ✅ Parallel execution (3-5x faster)
- ✅ Domain expertise (8 fire science specialists)
- ✅ DNA evolution (continuous learning)
- ✅ Live monitoring
- ✅ MCP integration (optional)

**Next Steps**:
1. Run setup if you haven't: `bash setup-wildfire-simulator-agents.sh`
2. Try your first agent: `bash run-agents-parallel.sh fbp-algorithm-agent`
3. Monitor progress: `bash monitor-agents.sh`
4. Review reports: Check `.agents/domain_agents/reports/`

**Happy coding with your AI agent team!** 🚀🔥
