#!/bin/bash
# Agent System Health Check

echo "=== Wildfire Simulator Agent System Health Check ==="
echo ""

# Check directories
echo "Directory Structure:"
for dir in .agents .agents/development_team .agents/domain_agents .agents/dna; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir"
    else
        echo "  ✗ $dir (missing)"
    fi
done
echo ""

# Check agent prompts
echo "Agent Prompts:"
AGENT_COUNT=$(find .agents -name "*-agent.txt" | wc -l)
echo "  Found: $AGENT_COUNT agent prompt files"
echo ""

# Check DNA genomes
echo "DNA Genomes:"
GENOME_COUNT=$(find .agents/dna -name "genome.json" 2>/dev/null | wc -l)
echo "  Found: $GENOME_COUNT genome files"
echo ""

# Check task files
echo "Task Files:"
TASK_COUNT=$(find .agents -name "*-tasks.json" 2>/dev/null | wc -l)
echo "  Found: $TASK_COUNT task definition files"
echo ""

# Check Python packages
echo "Python Environment:"
for pkg in numpy rasterio geopandas numba; do
    if python3 -c "import $pkg" 2>/dev/null; then
        echo "  ✓ $pkg"
    else
        echo "  ✗ $pkg (not installed)"
    fi
done
echo ""

echo "Health check complete!"
