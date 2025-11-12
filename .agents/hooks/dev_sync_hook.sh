#!/bin/bash
echo "🔄 Syncing Development Agent DNA with Review & Mentor systems..."

DEV_DNA=".agents/development_team/dna"
STATE_DB=".agents/state/state.db"
REVIEW_DIR=".agents/review/history"
LOGS=".agents/logs"

for AGENT in "$DEV_DNA"/*-agent; do
  NAME=$(basename "$AGENT")
  echo "🧬 Syncing $NAME..."
  cp -u "$AGENT/genome.json" ".agents/state/${NAME}_latest.json"
done

if [ -f "$LOGS/dev_feedback.log" ]; then
  echo "🪶 Appending developer feedback to mentor log..."
  cat "$LOGS/dev_feedback.log" >> "$LOGS/mentor_feedback.log"
  echo "" > "$LOGS/dev_feedback.log"
fi

TS=$(date -Iseconds | sed 's/:/-/g')
tar -czf "$REVIEW_DIR/DEV_STATE_$TS.tar.gz" "$DEV_DNA" || true
echo "✅ Development team state synced and archived at $REVIEW_DIR"
