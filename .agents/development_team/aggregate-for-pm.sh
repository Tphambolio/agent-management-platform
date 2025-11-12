#!/bin/bash
# Aggregates all agent reports for external PM review

OUTPUT_FILE=".agents/reports/EXTERNAL_PM_REPORT.md"

echo "# CrisisKit Multi-Agent Review Report" > $OUTPUT_FILE
echo "Generated: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

echo "## Agent Status Summary" >> $OUTPUT_FILE
for status_file in .agents/status/*.json; do
    if [ -f "$status_file" ]; then
        echo "### $(basename $status_file .json)" >> $OUTPUT_FILE
        cat $status_file >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
    fi
done

echo "## Detailed Reports" >> $OUTPUT_FILE
for report_file in .agents/reports/*.json; do
    if [ -f "$report_file" ]; then
        echo "### $(basename $report_file .json)" >> $OUTPUT_FILE
        cat $report_file >> $OUTPUT_FILE
        echo "" >> $OUTPUT_FILE
    fi
done

# Also include PM Dashboard if it exists
if [ -f ".agents/reports/PM_DASHBOARD.md" ]; then
    echo "## PM Dashboard" >> $OUTPUT_FILE
    cat .agents/reports/PM_DASHBOARD.md >> $OUTPUT_FILE
fi

echo ""
echo "Report generated: $OUTPUT_FILE"
echo "================================================"
cat $OUTPUT_FILE
