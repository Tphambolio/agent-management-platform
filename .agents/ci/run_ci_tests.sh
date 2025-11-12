#!/bin/bash
echo "🚦 Running local CI suite..."
python3 -m pytest tests --maxfail=1 --disable-warnings -q || { echo "❌ Unit tests failed"; exit 1; }
bash .agents/hooks/pre_validation_hook.sh || { echo "❌ Validation hook failed"; exit 1; }
python3 tools/guardian_agent.py || { echo "❌ Truth integrity check failed"; exit 1; }
echo "✅ CI suite passed all checks."