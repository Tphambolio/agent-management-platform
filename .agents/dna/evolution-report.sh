#!/bin/bash
AGENT_ID=$1
DNA_FILE=".agents/dna/$AGENT_ID/genome.json"
if [ ! -f "$DNA_FILE" ]; then
    echo "⚠️  DNA not found"
    exit 1
fi
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🧬 AGENT EVOLUTION REPORT: $AGENT_ID"
echo "╚════════════════════════════════════════════════════════════════╝"
SESSIONS=$(jq -r '.agent_metadata.total_sessions' "$DNA_FILE")
PATTERNS=$(jq -r '.experience_bank.patterns_known | length' "$DNA_FILE")
echo ""
echo "Sessions completed: $SESSIONS"
echo "Patterns learned: $PATTERNS"
echo "Learning velocity: $(jq -r '.evolution_metrics.learning_velocity' "$DNA_FILE")"
echo ""
