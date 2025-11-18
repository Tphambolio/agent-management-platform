# Claude Code CLI Integration

## Overview

Instead of paying for Anthropic API credits, this Agent Management Platform uses **Claude Code CLI** (the CLI you're already running!) to generate scientific reports.

## How It Works

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  localhost  │
│    :3000    │
└──────┬──────┘
       │
       ↓ API calls
┌──────────────┐
│   Backend    │ (FastAPI)
│  localhost   │
│    :8002     │
└──────┬───────┘
       │
       ↓ Creates task files
┌──────────────────────────────────────┐
│  /app/.agents/pending_tasks/         │
│  task_123.json ← Task request with   │
│  agent genome + research data        │
└──────┬───────────────────────────────┘
       │
       ↓ Watched by
┌──────────────────────────────────────┐
│  Claude Code CLI Task Watcher        │
│  (You running this script)           │
│  - Reads task files                  │
│  - Generates scientific reports      │
│  - Saves to results directory        │
└──────┬───────────────────────────────┘
       │
       ↓ Writes results
┌──────────────────────────────────────┐
│  /app/.agents/task_results/          │
│  task_123_result.json ← Report       │
└──────┬───────────────────────────────┘
       │
       ↓ Backend picks up
┌──────────────────┐
│  Database        │
│  Reports stored  │
└──────────────────┘
```

## Setup Instructions

### 1. Start the Backend
```bash
cd /home/rpas/agent-management-platform
docker-compose up -d
```

### 2. Start Claude Code CLI Watcher
In a separate terminal:
```bash
cd /home/rpas/agent-management-platform
python3 claude_code_watcher.py
```

This script will:
- Watch `/app/.agents/pending_tasks/` for new tasks
- Generate prompts for Claude Code CLI
- Save prompts to `/app/.agents/task_results/`

### 3. Generate Reports

When a new task appears, you'll see:
```
📋 Processing task: task_1234567890
   Agent: Fire Behavior Specialist Agent
   Title: Calculate Wildfire Spread Rate

💡 PROMPT SAVED TO: /app/.agents/task_results/task_1234567890_prompt.txt

ACTION REQUIRED:
1. Copy the prompt from the file above
2. Paste it into this Claude Code CLI session
3. Generate the scientific report
```

Then:
1. Open the prompt file
2. Copy the entire prompt
3. Paste it into Claude Code CLI (this conversation!)
4. I'll generate a complete scientific report
5. Save my response to the results file

### 4. Automate (Optional)

For fully automatic operation, you could:
- Use the Anthropic API (requires credits)
- Set up a local Claude model
- Create a web interface for manual review

## Benefits

✅ **No API Costs** - Uses Claude Code CLI you're already running
✅ **Real Scientific Reports** - Publication-quality with working code
✅ **Agent Expertise** - Loads genome files (29 training sessions for Backend Dev Agent!)
✅ **Code Learning** - Agents extract Python code from reports and add to skills
✅ **Web Research** - Brave Search API provides real research data

## Example Workflow

1. User creates task in frontend: "Calculate wildfire spread rate"
2. Backend fetches research via Brave API
3. Backend creates task file with research + agent genome
4. Watcher detects new task
5. You copy prompt and paste into Claude Code CLI
6. Claude generates scientific report with Python code
7. Report saved to results directory
8. Backend loads report into database
9. Code extractor finds Python code in report
10. Code added to agent's genome.json
11. Agent gets smarter with each task!

## Directory Structure

```
/home/rpas/agent-management-platform/
├── .agents/
│   ├── dna/                    # Agent genome files
│   │   ├── backend-developer-agent/
│   │   │   └── genome.json     # 29 training sessions!
│   │   ├── fire-behavior-specialist-agent/
│   │   │   └── genome.json     # 7 training sessions
│   │   └── ...
│   ├── pending_tasks/          # Task queue for Claude Code CLI
│   │   └── task_*.json
│   ├── task_results/           # Generated reports
│   │   ├── task_*_prompt.txt   # Prompts for you to copy
│   │   └── task_*_result.json  # Results you save
│   ├── memory/                 # Agent learning history
│   ├── datasets/               # Research data
│   └── artifacts/              # Code artifacts
├── backend/
├── frontend/
├── claude_code_watcher.py      # ← Run this!
└── README_CLAUDE_CODE_INTEGRATION.md
```

## Current Status

✅ Backend running with Brave API key (real web research)
✅ 12 agents loaded with genome data
✅ Code extraction system active
✅ Agent memory tracking
✅ Frontend + Backend connected
⏳ Waiting for you to run `claude_code_watcher.py`
⏳ Then tasks will flow through for report generation!

## Next Steps

1. Run the watcher: `python3 claude_code_watcher.py`
2. Create a test task in the frontend
3. Copy the generated prompt
4. Paste into Claude Code CLI
5. See the magic happen! 🎉
