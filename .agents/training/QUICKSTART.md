# Agent Training System - Quick Start

## Overview
Efficient agent training infrastructure with 1200 scenarios, progressive curriculum, and intelligent caching.

## Quick Start

### 1. Generate Scenarios (Fast - Minutes)
```bash
python3 tools/scenario_generator.py --level 1
```

### 2. Run Training (Automated - Overnight)
```bash
bash tools/auto_train.sh --level 1
```

### 3. Check Progress
```bash
python3 tools/training_curriculum.py --status
```

## Architecture

- **Scenario Generator**: Creates 1200 diverse fire scenarios
- **Pattern Extractor**: Local analysis (no LLM)
- **Batch Learning**: Efficient multi-scenario LLM analysis
- **Cache Manager**: 90%+ cache hit rate
- **Curriculum**: 5 progressive difficulty levels
- **Auto-Train**: Fully automated pipeline

## Training Levels

1. **Level 1**: Basic Fire Behavior (200 scenarios, 70% pass)
2. **Level 2**: Variable Conditions (250 scenarios, 65% pass)
3. **Level 3**: Extreme Conditions (300 scenarios, 60% pass)
4. **Level 4**: Complex Scenarios (250 scenarios, 55% pass)
5. **Level 5**: Edge Cases & Mega-Fires (200 scenarios, 50% pass)

## Key Features

- **Zero-cost local computation**
- **<20 LLM API calls total**
- **90%+ cache hit rate**
- **Progressive learning**
- **Automatic DNA updates**

## Files

- `tools/scenario_generator.py` - Generate scenarios
- `tools/pattern_extractor.py` - Analyze results
- `tools/batch_learning.py` - LLM batch analysis
- `tools/cache_manager.py` - Cache management
- `tools/training_curriculum.py` - Curriculum logic
- `tools/auto_train.sh` - Automated pipeline

## Next Steps

1. Generate Level 1 scenarios
2. Run auto-train overnight
3. Review extracted patterns
4. Advance to Level 2
