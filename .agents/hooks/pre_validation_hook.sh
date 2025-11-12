#!/bin/bash
set -euo pipefail
echo "🔍 Running pre-validation checks..."

# Truth guardian (hash verification)
if [ -f tools/truth_guardian.py ]; then
  python3 tools/guardian_permissions.py --agent truth_guardian --read "truth/*" ".agents/logs/*" --write ".agents/logs/truth_hashes.txt"
  python3 tools/truth_guardian.py
fi

# Frontend truth (network allowed)
if [ -f tools/frontend_truth_agent.py ]; then
  python3 tools/guardian_permissions.py --agent frontend_truth_agent --write ".agents/logs/frontend_truth_report.json" --needs-net
  python3 tools/frontend_truth_agent.py
fi

# Quick validation metrics
if [ -f tools/validation_agent.py ]; then
  python3 tools/guardian_permissions.py --agent validation_agent --read "outputs/*" ".agents/logs/*" "truth/*" --write ".agents/logs/validation_history.jsonl" "outputs/metrics.json"
  python3 tools/validation_agent.py
fi
