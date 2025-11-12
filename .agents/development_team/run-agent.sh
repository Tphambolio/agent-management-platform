#!/bin/bash
# Agent Runner Script for CrisisKit Multi-Agent System

AGENT_NAME=$1
AGENT_PROMPT=".agents/${AGENT_NAME}.txt"

if [ -z "$AGENT_NAME" ]; then
    echo "Usage: ./run-agent.sh [agent-name]"
    echo "Available agents:"
    echo "  - pm-orchestrator"
    echo "  - security-agent"
    echo "  - testing-agent"
    echo "  - performance-agent"
    echo "  - code-quality-agent"
    exit 1
fi

if [ ! -f "$AGENT_PROMPT" ]; then
    echo "Error: Agent prompt file not found: $AGENT_PROMPT"
    exit 1
fi

echo "=== Running $AGENT_NAME ==="
echo "Prompt file: $AGENT_PROMPT"
echo "Starting agent..."
echo ""

# Run Claude Code with the agent prompt content
claude "$(cat $AGENT_PROMPT)"

echo ""
echo "=== Agent $AGENT_NAME completed ==="
echo "Check .agents/reports/ for output"
echo "Check .agents/status/${AGENT_NAME}-status.json for status"
