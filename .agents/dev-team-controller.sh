#!/bin/bash
# =================================================================
# Development Team Controller
# Coordinates cleanup agents for the Wildfire Simulator project
# =================================================================

set -e

PROJECT_ROOT="/home/rpas/wildfire-simulator-v2"
AGENTS_DIR="$PROJECT_ROOT/.agents"
DEV_TEAM_DIR="$AGENTS_DIR/development_team"
TASKS_DIR="$DEV_TEAM_DIR/tasks"
REPORTS_DIR="$DEV_TEAM_DIR/reports"
STATUS_DIR="$DEV_TEAM_DIR/status"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Development Team Controller - Cleanup Coordinator    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Ensure directories exist
mkdir -p "$REPORTS_DIR" "$STATUS_DIR"

# Available agents
AGENTS=(
    "backend-cleanup-agent"
    "frontend-cleanup-agent"
    "refactoring-agent"
    "documentation-agent"
)

# Function to run a single agent
run_agent() {
    local AGENT_NAME=$1
    local AGENT_PROMPT="$AGENTS_DIR/${AGENT_NAME}.txt"

    if [ ! -f "$AGENT_PROMPT" ]; then
        echo -e "${RED}✗ Agent prompt not found: $AGENT_PROMPT${NC}"
        return 1
    fi

    if [ ! -f "$TASKS_DIR/${AGENT_NAME}-tasks.json" ]; then
        echo -e "${RED}✗ Task file not found for $AGENT_NAME${NC}"
        return 1
    fi

    echo -e "${GREEN}▶ Running $AGENT_NAME...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Run the agent via Claude Code
    cd "$PROJECT_ROOT"
    claude "$(cat $AGENT_PROMPT)"

    echo ""
    echo -e "${GREEN}✓ $AGENT_NAME completed${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Function to show agent status
show_status() {
    echo -e "${BLUE}Agent Status Summary:${NC}"
    echo ""
    for agent in "${AGENTS[@]}"; do
        local status_file="$STATUS_DIR/${agent}-status.json"
        if [ -f "$status_file" ]; then
            local status=$(jq -r '.status // "unknown"' "$status_file" 2>/dev/null || echo "unknown")
            local tasks_completed=$(jq -r '.tasks_completed | length' "$status_file" 2>/dev/null || echo "0")
            echo -e "  ${GREEN}●${NC} $agent: ${YELLOW}$status${NC} ($tasks_completed tasks completed)"
        else
            echo -e "  ${RED}○${NC} $agent: not started"
        fi
    done
    echo ""
}

# Function to aggregate reports
aggregate_reports() {
    echo -e "${BLUE}Aggregating Reports...${NC}"
    local SUMMARY_FILE="$REPORTS_DIR/CLEANUP_SUMMARY.md"

    cat > "$SUMMARY_FILE" <<EOF
# Development Team Cleanup Summary
Generated: $(date -Iseconds)

## Overview
This report summarizes the cleanup work performed by the development team agents.

EOF

    for agent in "${AGENTS[@]}"; do
        local report_file="$REPORTS_DIR/${agent}-report.json"
        if [ -f "$report_file" ]; then
            echo "## $agent" >> "$SUMMARY_FILE"
            echo "" >> "$SUMMARY_FILE"
            jq -r '"**Summary:** \(.summary // "N/A")\n\n**Files Modified:** \(.files_modified | length // 0)\n\n**Changes:**\n\(.changes_made[]? | "- \(.)")\n"' "$report_file" >> "$SUMMARY_FILE" 2>/dev/null || echo "No report data available" >> "$SUMMARY_FILE"
            echo "" >> "$SUMMARY_FILE"
        fi
    done

    echo -e "${GREEN}✓ Summary written to: $SUMMARY_FILE${NC}"
    echo ""
}

# Main menu
show_menu() {
    echo -e "${YELLOW}What would you like to do?${NC}"
    echo ""
    echo "  1) Run all agents sequentially"
    echo "  2) Run specific agent"
    echo "  3) Show status"
    echo "  4) Aggregate reports"
    echo "  5) Exit"
    echo ""
    read -p "Choose an option (1-5): " choice

    case $choice in
        1)
            echo ""
            echo -e "${GREEN}Running all agents...${NC}"
            echo ""
            for agent in "${AGENTS[@]}"; do
                run_agent "$agent"
                sleep 2
            done
            echo ""
            echo -e "${GREEN}✓ All agents completed${NC}"
            aggregate_reports
            ;;
        2)
            echo ""
            echo "Available agents:"
            for i in "${!AGENTS[@]}"; do
                echo "  $((i+1))) ${AGENTS[$i]}"
            done
            echo ""
            read -p "Choose agent (1-${#AGENTS[@]}): " agent_choice
            if [ "$agent_choice" -ge 1 ] && [ "$agent_choice" -le "${#AGENTS[@]}" ]; then
                run_agent "${AGENTS[$((agent_choice-1))]}"
            else
                echo -e "${RED}Invalid choice${NC}"
            fi
            ;;
        3)
            echo ""
            show_status
            ;;
        4)
            echo ""
            aggregate_reports
            ;;
        5)
            echo ""
            echo -e "${BLUE}Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
    echo ""
    show_menu
}

# Check if running in interactive mode
if [ -t 0 ]; then
    show_menu
else
    # Non-interactive: run all agents
    echo "Running in non-interactive mode..."
    for agent in "${AGENTS[@]}"; do
        run_agent "$agent"
    done
    aggregate_reports
fi
