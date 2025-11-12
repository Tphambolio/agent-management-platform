#!/bin/bash
# ============================================================================
#  POST-SESSION HOOK - Automatic DNA Evolution
#  Purpose: Run this manually at the end of each development session
#  Usage: ./.agents/hooks/post-session.sh "Session summary message"
# ============================================================================

SESSION_SUMMARY="${1:-Manual session completion}"
AGENT_ID="backend-developer-agent"

cd "$(dirname "$0")/../.." || exit 1

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🧬 POST-SESSION DNA EVOLUTION STARTING                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Session Summary: $SESSION_SUMMARY"
echo ""

# Run evolution
./.agents/evolve.sh

# Optional: Git commit the DNA changes
if [ -d .git ]; then
    echo ""
    read -p "Commit DNA changes to git? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .agents/
        git commit -m "🧬 Agent DNA Evolution: $SESSION_SUMMARY"
        echo "✓ DNA changes committed to git"
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         ✅ POST-SESSION COMPLETE - DNA EVOLVED                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next session will start with updated DNA!"
