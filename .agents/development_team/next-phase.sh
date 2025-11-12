#!/bin/bash
# Advances to next phase based on PM approval

echo "Select next phase:"
echo "1) Continue SECURITY tasks"
echo "2) Start CODE QUALITY tasks"
echo "3) Start TESTING tasks"
echo "4) Start PERFORMANCE tasks"
echo "5) Start DEPLOYMENT tasks"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "SECURITY" > .agents/current-phase.txt
        echo "Running security-agent..."
        ./.agents/run-agent.sh security-agent
        ;;
    2)
        echo "CODE_QUALITY" > .agents/current-phase.txt
        echo "Running code-quality-agent..."
        ./.agents/run-agent.sh code-quality-agent
        ;;
    3)
        echo "TESTING" > .agents/current-phase.txt
        echo "Running testing-agent..."
        ./.agents/run-agent.sh testing-agent
        ;;
    4)
        echo "PERFORMANCE" > .agents/current-phase.txt
        echo "Running performance-agent..."
        ./.agents/run-agent.sh performance-agent
        ;;
    5)
        echo "DEPLOYMENT" > .agents/current-phase.txt
        echo "Creating deployment agent..."
        echo "⚠️ Deployment agent not yet created"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
