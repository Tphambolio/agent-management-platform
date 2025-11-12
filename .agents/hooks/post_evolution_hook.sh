#!/bin/bash
set -euo pipefail
echo "🧠 Post-evolution phase..."

if [ -f tools/memory_agent.py ]; then
  python3 tools/guardian_permissions.py --agent memory_agent --read ".agents/dna/*" ".agents/logs/*" "outputs/*" --write "outputs/reports/memory_summary.json"
  python3 tools/memory_agent.py
fi

if [ -f tools/mentor_agent.py ]; then
  python3 tools/guardian_permissions.py --agent mentor_agent --read "outputs/reports/memory_summary.json" ".agents/logs/*" --write ".agents/logs/mentor_advice.md"
  python3 tools/mentor_agent.py
fi

if [ -f tools/dashboard_agent.py ]; then
  python3 tools/guardian_permissions.py --agent dashboard_agent --read "outputs/*" ".agents/logs/*" --write "outputs/dashboard/*"
  python3 tools/dashboard_agent.py
fi

# Optional quality agents (ignore exit on errors here)
( python3 tools/anomaly_agent.py 2>/dev/null || true )
( python3 tools/snapshot_agent.py 2>/dev/null || true )
( python3 tools/regression_agent.py 2>/dev/null || true )

# Run audit drop
if [ -f tools/run_audit_drop.py ]; then
  python3 tools/run_audit_drop.py
fi
