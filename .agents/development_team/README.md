# Development Team Agent System

A multi-agent system for automated code cleanup, refactoring, and improvement of the Wildfire Simulator project.

## Overview

The development team consists of specialized AI agents that work together to maintain and improve code quality:

- **Backend Cleanup Agent**: Python code quality, linting, type hints
- **Frontend Cleanup Agent**: HTML/CSS/JS cleanup, performance optimization
- **Refactoring Agent**: Code architecture and structural improvements
- **Documentation Agent**: Docstrings, README files, API documentation

## Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
bash .agents/dev-team-controller.sh
```

### Option 2: Quick Cleanup Script
```bash
bash cleanup.sh
```

### Option 3: Run Specific Agent
```bash
cd /home/rpas/wildfire-simulator-v2
claude "$(cat .agents/backend-cleanup-agent.txt)"
```

## How It Works

### 1. Task Assignment
Each agent has a task file defining specific work items:
- `.agents/development_team/tasks/backend-cleanup-agent-tasks.json`
- `.agents/development_team/tasks/frontend-cleanup-agent-tasks.json`
- `.agents/development_team/tasks/refactoring-agent-tasks.json`
- `.agents/development_team/tasks/documentation-agent-tasks.json`

### 2. Agent Execution
Agents read their tasks, execute them systematically, and update:
- **Status**: `.agents/development_team/status/[agent]-status.json`
- **Reports**: `.agents/development_team/reports/[agent]-report.json`

### 3. DNA Evolution
Agents learn from their work and update their genome:
- `.agents/development_team/dna/[agent]/genome.json`
- Tracks skills, patterns, and experience

### 4. Sync & Review
After completion, the dev sync hook integrates results:
- Archives DNA state
- Merges feedback with mentor system
- Updates review history

## Directory Structure

```
.agents/
├── development_team/
│   ├── dna/                      # Agent DNA/genome storage
│   │   ├── backend-developer-agent/
│   │   ├── ui-engineer-agent/
│   │   ├── data-engineer-agent/
│   │   └── qa-engineer-agent/
│   ├── tasks/                    # Task definitions
│   ├── reports/                  # Agent outputs
│   ├── status/                   # Current status
│   └── README.md                 # This file
├── hooks/
│   └── dev_sync_hook.sh         # Post-execution sync
├── backend-cleanup-agent.txt     # Agent prompts
├── frontend-cleanup-agent.txt
├── refactoring-agent.txt
└── documentation-agent.txt
```

## Agent Responsibilities

### Backend Cleanup Agent
- Remove unused imports and dead code
- Fix linting errors (pylint, flake8)
- Add type hints
- Improve error handling and logging
- Optimize database queries

### Frontend Cleanup Agent
- Fix console errors and warnings
- Remove unused CSS
- Optimize asset loading
- Improve accessibility
- Consolidate duplicate styles

### Refactoring Agent
- Break down large files (>500 lines)
- Extract duplicate code
- Reduce cyclomatic complexity
- Improve naming conventions
- Apply design patterns

### Documentation Agent
- Add docstrings to functions/classes
- Update README files
- Document API endpoints
- Add inline comments for complex logic
- Create architecture guides

## Monitoring Progress

### Check Status
```bash
cat .agents/development_team/status/backend-cleanup-agent-status.json | jq
```

### View Reports
```bash
cat .agents/development_team/reports/backend-cleanup-agent-report.json | jq
```

### View Summary
```bash
cat .agents/development_team/reports/CLEANUP_SUMMARY.md
```

### Check DNA Evolution
```bash
cat .agents/development_team/dna/backend-developer-agent/genome.json | jq
```

## Integration with Evolution Pipeline

The development team automatically syncs with the main evolution pipeline:

1. Run cleanup: `./cleanup.sh`
2. Evolution runs: `./run_all.sh`
3. Post-evolution hook executes
4. Dev sync hook archives DNA and merges feedback
5. Dashboard updates: `python3 tools/developer_dashboard.py`

## Customization

### Add New Tasks
Edit task files in `.agents/development_team/tasks/[agent]-tasks.json`:

```json
{
  "task_id": "backend-005",
  "priority": "high",
  "status": "pending",
  "objective": "Your task description",
  "scope": {
    "files": ["file1.py", "file2.py"],
    "directories": ["tools"],
    "exclusions": ["venv"]
  },
  "success_criteria": [
    "Measurable outcome 1",
    "Measurable outcome 2"
  ]
}
```

### Create New Agent
1. Create prompt: `.agents/new-agent.txt`
2. Create tasks: `.agents/development_team/tasks/new-agent-tasks.json`
3. Add to controller: Edit `.agents/dev-team-controller.sh`

## Best Practices

1. **Run agents sequentially** to avoid conflicts
2. **Review changes** before committing
3. **Run tests** after each agent completes
4. **Commit frequently** with descriptive messages
5. **Monitor DNA evolution** to track agent learning

## Troubleshooting

### Agent won't run
- Check task file exists and is valid JSON
- Verify agent prompt file exists
- Ensure Claude Code is available in PATH

### Tasks not completing
- Check `.agents/development_team/status/[agent]-status.json`
- Look for "blocked" status and resolve dependencies
- Review error messages in agent output

### Reports not generated
- Verify `.agents/development_team/reports/` directory exists
- Check agent has write permissions
- Ensure task success criteria are met

## Dashboard

Monitor all agents via web interface:

```bash
python3 tools/developer_dashboard.py
```

Visit: http://localhost:8085

## Support

For issues or questions:
- Check logs: `.agents/logs/`
- Review task definitions
- Consult main project documentation
