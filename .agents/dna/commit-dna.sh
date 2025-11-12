#!/bin/bash
AGENT_ID=$1
SUMMARY=$2
DNA_FILE=".agents/dna/$AGENT_ID/genome.json"
if [ ! -f "$DNA_FILE" ]; then
    echo "⚠️  DNA not found"
    exit 1
fi
jq ".agent_metadata.total_sessions += 1 |
    .session_memory.last_session_summary = \"$SUMMARY\"" \
    "$DNA_FILE" > "$DNA_FILE.tmp"
mv "$DNA_FILE.tmp" "$DNA_FILE"
echo "✓ DNA committed for $AGENT_ID"
echo "  Summary: $SUMMARY"
