# CrisisKit Multi-Agent Workflow

## Current Status
- Phase: SECURITY (In Progress)
- Last Agent: security-agent
- Pending: MapBox & MapTiler token rotation

## Workflow Loop

### Step 1: Agent Completes Work
Agent outputs report to `.agents/reports/`

### Step 2: Generate PM Report
Run: `./.agents/pm-controller.sh`

### Step 3: Human Copies Report
Copy everything from pm-controller output

### Step 4: Paste to External PM
Paste into Claude web chat

### Step 5: PM Reviews & Approves
External PM provides:
- Approval/Concerns
- Next agent to run
- Specific instructions

### Step 6: Human Pastes PM Instructions
Paste PM's response back into Claude terminal

### Step 7: Agent Executes
Agent reads instructions and executes tasks

### Step 8: Repeat Loop
Go back to Step 1

## Quick Commands

# Generate PM report
./.agents/pm-controller.sh

# Run specific agent
./.agents/run-agent.sh [agent-name]

# Check agent status
cat .agents/status/*.json

# View latest reports
ls -ltr .agents/reports/
