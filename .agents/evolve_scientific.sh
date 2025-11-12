#!/bin/bash
# Scientific Evolution Cycle - Driven by Real Fire Validation
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔬 SCIENTIFIC EVOLUTION CYCLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CYCLE_START=$(date +%s)

# Phase 1: Run model with current parameters
echo "📊 PHASE 1: Running Fire Model"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 tools/fire_model_agent_adaptive.py || { echo "❌ Model run failed"; exit 1; }
echo ""

# Phase 2: Scientific validation against real fires
echo "📋 PHASE 2: Scientific Validation (Fort McMurray 2016)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 tools/scientific_reviewer_agent.py --once || echo "⚠️ Validation found issues"
echo ""

# Phase 3: DNA Learning - Update agent knowledge
echo "🧬 PHASE 3: DNA Learning"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 tools/dna_learning_agent.py || echo "⚠️ DNA learning had issues"
echo ""

# Phase 4: Append metrics to validation history
echo "📈 PHASE 4: Recording Progress"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOG_DIR=".agents/logs"
mkdir -p "$LOG_DIR"
METRICS="outputs/metrics.json"
HIST="$LOG_DIR/validation_history.jsonl"

if [ -f "$METRICS" ]; then
    cat "$METRICS" >> "$HIST"
    echo "✅ Metrics appended to history"
else
    echo "⚠️ No metrics file found"
fi
echo ""

# Phase 5: Update genome session count
DNA=".agents/dna/backend-developer-agent/genome.json"
if [ -f "$DNA" ]; then
    python3 - <<PY
import json
dna = json.load(open("$DNA"))
dna["agent_metadata"]["total_sessions"] = dna["agent_metadata"].get("total_sessions", 0) + 1
json.dump(dna, open("$DNA", "w"), indent=2)
print(f"🔢 Evolution cycles: {dna['agent_metadata']['total_sessions']}")
PY
fi
echo ""

# Phase 6: Generate improvement report
echo "📊 PHASE 6: Evolution Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 - <<'PYREPORT'
import json
from pathlib import Path

# Load latest scientific review
reviews_file = Path(".agents/logs/scientific_reviews.jsonl")
if reviews_file.exists():
    with open(reviews_file, 'r') as f:
        lines = f.readlines()
        if lines:
            latest_review = json.loads(lines[-1])

            print("VALIDATION STATUS:")
            print(f"  Score: {latest_review['score']}/100")
            print(f"  Assessment: {latest_review['overall_assessment']}")
            print()

            if latest_review['validations_passed']:
                print(f"✅ Passed: {len(latest_review['validations_passed'])} checks")

            if latest_review['issues']:
                print(f"❌ Issues: {len(latest_review['issues'])} identified")
                for issue in latest_review['issues'][:3]:
                    print(f"   • {issue}")

            print()

            # Show improvement tasks
            tasks_dir = Path(".agents/tasks")
            if tasks_dir.exists():
                task_files = list(tasks_dir.glob("*.md"))
                print(f"📋 IMPROVEMENT TASKS: {len(task_files)} identified")
                for task in task_files:
                    task_id = task.stem
                    print(f"   • {task_id}")
                print()

PYREPORT

CYCLE_END=$(date +%s)
DURATION=$((CYCLE_END - CYCLE_START))

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ EVOLUTION CYCLE COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Duration: ${DURATION}s"
echo ""
echo "Summary:"
echo "  • Model ran with adaptive parameters"
echo "  • Validated against Fort McMurray 2016 (real fire)"
echo "  • Agent DNA updated with learnings"
echo "  • Improvement tasks identified"
echo ""
echo "Next Steps:"
echo "  1. Review improvement tasks: .agents/tasks/"
echo "  2. Implement highest priority fixes"
echo "  3. Re-run evolution to validate improvements"
echo ""
echo "View detailed logs:"
echo "  • .agents/logs/scientific_reviews.jsonl"
echo "  • .agents/logs/mentor_feedback.log"
echo "  • .agents/dna/*/genome.json"
echo ""
