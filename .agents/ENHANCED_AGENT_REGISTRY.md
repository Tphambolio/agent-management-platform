# Wildfire Simulator Enhanced Agent Registry

## Overview
Complete registry of all agents in the multi-agent system, including development team, coordination, and domain-specific specialists.

**Last Updated**: 2025-10-28
**Total Agents**: 25+
**System Status**: ✅ Fully Operational

---

## Domain Specialist Agents (NEW)

### 1. FBP-Algorithm-Agent
**Purpose**: Canadian Forest Fire Behavior Prediction (FBP) System expert
**Location**: `.agents/domain_agents/fbp-algorithm-agent.txt`
**Expertise**:
- All 18 fuel type models (C1-C7, D1-D2, M1-M4, O1a-O1b, S1-S3)
- Rate of spread (ROS) equations
- Crown fire behavior
- BUI effects and extreme conditions

**Key Tasks**:
- Audit FBP implementation accuracy
- Validate extreme BUI handling (BUI > 150)
- Optimize FBP calculations
- Create validation test suites

**Status File**: `.agents/domain_agents/status/fbp-algorithm-agent-status.json`
**Reports**: `.agents/domain_agents/reports/fbp-algorithm-agent-report.json`

---

### 2. Weather-Data-Agent
**Purpose**: Fire Weather Index (FWI) System and weather processing expert
**Location**: `.agents/domain_agents/weather-data-agent.txt`
**Expertise**:
- FWI components (FFMC, DMC, DC, ISI, BUI, FWI)
- Hourly FWI methods
- Multi-day weather sequences
- Rain effects on fuel moisture

**Key Tasks**:
- Validate FWI calculations
- Test extreme fire weather (Jasper 2024)
- Verify FWI-to-FBP integration
- Validate hourly FWI methods

**Status File**: `.agents/domain_agents/status/weather-data-agent-status.json`
**Reports**: `.agents/domain_agents/reports/weather-data-agent-report.json`

---

### 3. Spatial-Analysis-Agent
**Purpose**: GIS operations and spatial data processing expert
**Location**: `.agents/domain_agents/spatial-analysis-agent.txt`
**Expertise**:
- Rasterio, geopandas, GDAL operations
- Fuel map processing
- DEM/slope/aspect calculations
- Coordinate transformations

**Key Tasks**:
- Audit spatial data pipeline
- Validate fuel map loading
- Optimize raster operations
- Ensure data quality

**Status File**: `.agents/domain_agents/status/spatial-analysis-agent-status.json`
**Reports**: `.agents/domain_agents/reports/spatial-analysis-agent-report.json`

---

### 4. Performance-Tuning-Agent
**Purpose**: Code optimization and performance expert
**Location**: `.agents/domain_agents/performance-tuning-agent.txt`
**Expertise**:
- Numba JIT compilation
- NumPy vectorization
- Parallel processing
- Memory optimization

**Key Tasks**:
- Profile performance bottlenecks
- Optimize hot-path functions
- Parallelize Monte Carlo simulations
- Reduce memory overhead

**Status File**: `.agents/domain_agents/status/performance-tuning-agent-status.json`
**Reports**: `.agents/domain_agents/reports/performance-tuning-agent-report.json`

---

### 5. Spotting-Model-Agent
**Purpose**: Ember transport and spotting fire expert
**Location**: `.agents/domain_agents/spotting-model-agent.txt`
**Expertise**:
- Ember generation and lofting
- Trajectory modeling
- Ignition probability
- Integration with fire spread

**Key Tasks**:
- Validate spotting physics
- Compare against historical events
- Optimize spotting calculations
- Test edge cases

**Status File**: `.agents/domain_agents/status/spotting-model-agent-status.json`
**Reports**: `.agents/domain_agents/reports/spotting-model-agent-report.json`

---

### 6. Monte-Carlo-Agent
**Purpose**: Stochastic simulation and statistical aggregation expert
**Location**: `.agents/domain_agents/monte-carlo-agent.txt`
**Expertise**:
- Monte Carlo design
- Statistical sampling
- Burn probability calculation
- Uncertainty quantification

**Key Tasks**:
- Validate statistical methods
- Analyze convergence
- Optimize parallel execution
- Ensure reproducibility

**Status File**: `.agents/domain_agents/status/monte-carlo-agent-status.json`
**Reports**: `.agents/domain_agents/reports/monte-carlo-agent-report.json`

---

### 7. Scientific-Validation-Agent
**Purpose**: Scientific accuracy and benchmark validation expert
**Location**: `.agents/domain_agents/scientific-validation-agent.txt`
**Expertise**:
- Fire science literature
- Model validation methodologies
- Historical fire event analysis
- Accuracy metrics

**Key Tasks**:
- Compare against historical fires
- Validate benchmarks
- Document scientific assumptions
- Ensure citations are complete

**Status File**: `.agents/domain_agents/status/scientific-validation-agent-status.json`
**Reports**: `.agents/domain_agents/reports/scientific-validation-agent-report.json`

---

### 8. Visualization-Agent
**Purpose**: Data visualization and dashboard creation expert
**Location**: `.agents/domain_agents/visualization-agent.txt`
**Expertise**:
- Matplotlib advanced plotting
- Geospatial visualization
- Fire behavior animations
- Interactive dashboards

**Key Tasks**:
- Create burn probability maps
- Generate fire spread animations
- Build monitoring dashboard
- Ensure publication-quality figures

**Status File**: `.agents/domain_agents/status/visualization-agent-status.json`
**Reports**: `.agents/domain_agents/reports/visualization-agent-report.json`

---

## Development Team Agents (EXISTING)

### Backend Cleanup Agent
**Location**: `.agents/backend-cleanup-agent.txt`
**Purpose**: Python code quality, linting, type hints
**Tasks**: `.agents/development_team/tasks/backend-cleanup-agent-tasks.json`

### Frontend Cleanup Agent
**Location**: `.agents/frontend-cleanup-agent.txt`
**Purpose**: HTML/CSS/JS cleanup, performance optimization
**Tasks**: `.agents/development_team/tasks/frontend-cleanup-agent-tasks.json`

### Refactoring Agent
**Location**: `.agents/refactoring-agent.txt`
**Purpose**: Code architecture and structural improvements
**Tasks**: `.agents/development_team/tasks/refactoring-agent-tasks.json`

### Documentation Agent
**Location**: `.agents/documentation-agent.txt`
**Purpose**: Docstrings, README files, API documentation
**Tasks**: `.agents/development_team/tasks/documentation-agent-tasks.json`

---

## Coordination Agents (EXISTING)

### PM Orchestrator
**Location**: `.agents/development_team/pm-orchestrator.txt`
**Purpose**: Project coordination, task assignment, progress monitoring
**Tasks**: Creates tasks for other agents

### Security Agent
**Location**: `.agents/development_team/security-agent.txt`
**Purpose**: Security audits, vulnerability detection
**Tasks**: `.agents/development_team/tasks/security-agent-tasks.json`

### Testing Agent
**Location**: `.agents/development_team/testing-agent.txt`
**Purpose**: QA, test coverage, functionality testing
**Tasks**: `.agents/development_team/tasks/testing-agent-tasks.json`

### Performance Agent
**Location**: `.agents/development_team/performance-agent.txt`
**Purpose**: General performance analysis (complements Performance-Tuning-Agent)
**Tasks**: `.agents/development_team/tasks/performance-agent-tasks.json`

### Code Quality Agent
**Location**: `.agents/development_team/code-quality-agent.txt`
**Purpose**: Code standards, best practices enforcement
**Tasks**: `.agents/development_team/tasks/code-quality-agent-tasks.json`

---

## Core System Agents (EXISTING)

- **Fire Model Agent**: `tools/fire_model_agent.py` - Execute fire simulations
- **Dataset Agent**: `tools/dataset_agent.py` - Data management
- **Validation Agent**: Validates simulation outputs
- **Memory Agent**: Knowledge persistence
- **Mentor Agent**: Guidance system
- **Dashboard Agent**: System monitoring
- **Anomaly Agent**: Outlier detection
- **Snapshot Agent**: State management
- **Regression Agent**: Testing
- **Review Agent**: Code review
- **Frontend Reviewer**: UI review
- **Scientific Reviewer**: Science validation

---

## Agent Coordination Protocol

### Task Assignment
1. Each agent reads from: `.agents/[team]/tasks/[agent-name]-tasks.json`
2. Task format: Priority, objective, scope, success criteria

### Status Reporting
1. Each agent writes to: `.agents/[team]/status/[agent-name]-status.json`
2. Status includes: running/completed/failed, progress %, timestamp

### Report Generation
1. Each agent outputs to: `.agents/[team]/reports/[agent-name]-report.json`
2. Report includes: findings, changes, validation results

### DNA Evolution
1. Agent learning stored in: `.agents/[team]/dna/[agent-name]/genome.json`
2. Tracks: skills, patterns, techniques, pitfalls

---

## Running Agents

### Single Agent
```bash
bash .agents/development_team/run-agent.sh [agent-name]
```

### Multiple Agents in Parallel
```bash
bash run-agents-parallel.sh [agent1] [agent2] [agent3]
```

### Monitor All Agents (Live Dashboard)
```bash
bash monitor-agents.sh
```

### Example Usage
```bash
# Run domain specialists in parallel
bash run-agents-parallel.sh fbp-algorithm-agent weather-data-agent spatial-analysis-agent

# Monitor their progress
bash monitor-agents.sh
```

---

## Agent Collaboration Matrix

| Agent | Collaborates With |
|-------|-------------------|
| FBP-Algorithm | Weather-Data, Scientific-Validation, Performance-Tuning |
| Weather-Data | FBP-Algorithm, Monte-Carlo, Scientific-Validation |
| Spatial-Analysis | FBP-Algorithm, Monte-Carlo, Visualization |
| Performance-Tuning | FBP-Algorithm, Monte-Carlo, Spatial-Analysis |
| Spotting-Model | FBP-Algorithm, Weather-Data, Scientific-Validation |
| Monte-Carlo | Performance-Tuning, Weather-Data, Spatial-Analysis |
| Scientific-Validation | All domain agents |
| Visualization | Monte-Carlo, Spatial-Analysis, Scientific-Validation |

---

## Quick Reference

### Domain Agents Directory
```
.agents/domain_agents/
├── [agent-name].txt              # Agent prompts
├── tasks/[agent-name]-tasks.json # Task definitions
├── status/[agent-name]-status.json # Current status
├── reports/[agent-name]-report.json # Output reports
└── dna/[agent-name]/             # Learning DNA
```

### Development Team Directory
```
.agents/development_team/
├── [agent-name].txt              # Agent prompts
├── tasks/[agent-name]-tasks.json # Task definitions
├── status/[agent-name]-status.json # Current status
├── reports/[agent-name]-report.json # Output reports
└── dna/[agent-name]/             # Learning DNA
```

---

## System Health Check
```bash
bash .agents/health-check.sh
```

---

**Total Agent Count**: 25+ agents
**Domain Specialists**: 8 (NEW)
**Development Team**: 4
**Coordination**: 5
**Core System**: 12+

**System Architecture**: See `.agents/ARCHITECTURE.md`
**Enhancement Proposal**: See `.agents/MULTI_AGENT_ENHANCEMENT_PROPOSAL.md`
**DNA System**: See `.agents/AGENT_DNA_SUMMARY.md`
