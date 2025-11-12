#!/bin/bash
echo "🔍 Running pre-commit tests..."
bash .agents/ci/run_ci_tests.sh || { echo "❌ Pre-commit CI failed"; exit 1; }
echo "✅ Pre-commit tests passed."