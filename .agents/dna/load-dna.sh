#!/bin/bash
AGENT_ID=$1
DNA_FILE=".agents/dna/$AGENT_ID/genome.json"
if [ ! -f "$DNA_FILE" ]; then
    echo "⚠️  DNA not found. Run: ./.agents/dna/init-agent.sh $AGENT_ID <role>"
    exit 1
fi
echo "🧬 Loading DNA for $AGENT_ID..."
SESSION=$(jq -r '.agent_metadata.total_sessions' "$DNA_FILE")
echo "   Sessions completed: $SESSION"
echo "   Skills:"
jq -r '.skills.technical | to_entries[] | "     \(.key): Level \(.value.level)"' "$DNA_FILE" 2>/dev/null
echo "   Patterns known:"
jq -r '.experience_bank.patterns_known[]' "$DNA_FILE" 2>/dev/null | head -5 | sed 's/^/     • /'
echo "✓ DNA loaded. Agent ready with full context."
