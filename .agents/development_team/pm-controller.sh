#!/bin/bash
# PM Controller - Manages workflow between external PM and agents

PHASE_FILE=".agents/current-phase.txt"
REPORT_FILE=".agents/reports/LATEST_REPORT.md"

# Read current phase
if [ -f "$PHASE_FILE" ]; then
    CURRENT_PHASE=$(cat "$PHASE_FILE")
else
    CURRENT_PHASE="SECURITY"
fi

echo "=== CrisisKit PM Controller ==="
echo "Current Phase: $CURRENT_PHASE"
echo ""
echo "Aggregating latest reports for external PM review..."
echo ""

# Aggregate all reports
./.agents/aggregate-for-pm.sh

echo ""
echo "================================================"
echo "NEXT STEPS:"
echo "================================================"
echo ""
echo "1. COPY the report above"
echo "2. PASTE it to your external PM (Claude web chat)"
echo "3. WAIT for PM approval and next instructions"
echo "4. PASTE PM's instructions back here"
echo ""
echo "Current phase will auto-advance after PM approval."
