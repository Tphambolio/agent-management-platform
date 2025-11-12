#!/bin/bash
echo "🧬 Starting Evolution Cycle (Phase 10 - Adaptive Mode)"
python3 tools/dataset_agent.py

# Use adaptive fire model agent that consumes reviewer feedback
python3 tools/fire_model_agent_adaptive.py

# Append metrics to validation history
LOG_DIR=".agents/logs"
mkdir -p "$LOG_DIR"
METRICS="outputs/metrics.json"
HIST="$LOG_DIR/validation_history.jsonl"
cat "$METRICS" >> "$HIST"

# Increment genome sessions
DNA=".agents/dna/backend-developer-agent/genome.json"
if [ -f "$DNA" ]; then
  python3 - <<PY
import json; f="$DNA"
dna=json.load(open(f))
dna["agent_metadata"]["total_sessions"]=dna["agent_metadata"].get("total_sessions",0)+1
json.dump(dna,open(f,"w"),indent=2)
print("🔢 Genome sessions:", dna["agent_metadata"]["total_sessions"])
PY
fi

echo "✅ Evolution cycle complete."
