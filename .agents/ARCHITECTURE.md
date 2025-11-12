# Multi-Agent System Architecture

## Overview

The Wildfire Simulator uses a sophisticated multi-agent system for continuous improvement, quality assurance, and automated development. This document explains the architecture, agent roles, and workflows.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Wildfire Simulator Core                      │
│                  (Fire Behavior Simulation)                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Ecosystem                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Fire      │  │  Dataset    │  │  Validation │           │
│  │   Model     │  │   Agent     │  │   Agent     │           │
│  │   Agent     │  └─────────────┘  └─────────────┘           │
│  └─────────────┘                                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Memory     │  │   Mentor    │  │  Dashboard  │           │
│  │   Agent     │  │   Agent     │  │   Agent     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Anomaly    │  │  Snapshot   │  │  Regression │           │
│  │   Agent     │  │   Agent     │  │   Agent     │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Review     │  │  Frontend   │  │ Scientific  │           │
│  │   Agent     │  │  Reviewer   │  │  Reviewer   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                Development Team Agents                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Backend    │  │   Frontend   │  │ Refactoring  │         │
│  │   Cleanup    │  │   Cleanup    │  │    Agent     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐                                              │
│  │Documentation │                                              │
│  │    Agent     │                                              │
│  └──────────────┘                                              │
└─────────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DNA & Evolution                            │
│         (Agent Learning & Knowledge Management)                 │
└─────────────────────────────────────────────────────────────────┘
```

## Core Agents

### 1. Fire Model Agent
**Purpose**: Runs fire behavior simulations and generates predictions

**Location**: `tools/fire_model_agent.py`

**Responsibilities**:
- Execute fire spread simulations
- Generate burn probability maps
- Calculate fire intensity and rate of spread
- Output GeoTIFF layers for analysis

**Outputs**:
- `outputs/fire_layers/fire_spread.tif`
- `outputs/fire_layers/burn_probability.tif`
- Intensity and rate-of-spread rasters

### 2. Dataset Agent
**Purpose**: Manages training and validation data

**Location**: `tools/dataset_agent.py`

**Responsibilities**:
- Load real fire datasets
- Prepare training/validation splits
- Manage ground truth data
- Provide data loaders for model training

**Outputs**:
- Prepared datasets in standardized format
- Data quality reports

### 3. Validation Agent
**Purpose**: Validates simulation outputs against ground truth

**Location**: `tools/validation_agent.py`

**Responsibilities**:
- Compare simulations to real fire data
- Calculate RMSE, IoU, and other metrics
- Track accuracy over time
- Trigger evolution when improvements detected

**Outputs**:
- `.agents/logs/validation_history.jsonl`
- Metrics comparing predicted vs actual

### 4. Memory Agent
**Purpose**: Maintains system memory and learning history

**Location**: `tools/memory_agent.py`

**Responsibilities**:
- Store successful parameter combinations
- Track evolution history
- Maintain agent state across sessions
- Provide context for decision-making

**Outputs**:
- `.agents/memory/` directory
- Historical performance data

### 5. Mentor Agent
**Purpose**: Provides guidance and feedback to other agents

**Location**: `tools/mentor_agent.py`

**Responsibilities**:
- Analyze agent performance
- Suggest improvements
- Guide evolution direction
- Resolve conflicts between agents

**Outputs**:
- `.agents/logs/mentor_feedback.log`
- Guidance for model improvements

### 6. Dashboard Agent
**Purpose**: Generates visualization dashboards

**Location**: `tools/dashboard_agent.py`

**Responsibilities**:
- Create interactive HTML dashboards
- Visualize metrics over time
- Display current simulation status
- Provide web interface for monitoring

**Outputs**:
- `outputs/dashboard/index.html`
- Real-time status updates

### 7. Anomaly Agent
**Purpose**: Detects and flags unusual behavior

**Location**: `tools/anomaly_agent.py`

**Responsibilities**:
- Monitor simulation outputs for anomalies
- Detect degraded performance
- Alert when metrics deviate from expected
- Trigger investigations

**Outputs**:
- `.agents/logs/anomalies.jsonl`
- Anomaly reports and alerts

### 8. Snapshot Agent
**Purpose**: Creates versioned snapshots of agent state

**Location**: `tools/snapshot_agent.py`

**Responsibilities**:
- Snapshot DNA and parameters periodically
- Enable rollback to previous states
- Track evolution genealogy
- Archive successful configurations

**Outputs**:
- `.agents/snapshots/` directory
- Timestamped agent states

### 9. Regression Agent
**Purpose**: Prevents quality regressions

**Location**: `tools/regression_agent.py`

**Responsibilities**:
- Compare current vs previous performance
- Flag when metrics worsen
- Block deployments with regressions
- Maintain quality thresholds

**Outputs**:
- Regression test results
- Performance comparison reports

### 10. Review Agent
**Purpose**: Intelligent output review and quality control

**Location**: `tools/intelligent_reviewer_agent.py`

**Responsibilities**:
- Analyze simulation outputs comprehensively
- Provide actionable feedback
- Score output quality
- Suggest specific improvements

**Outputs**:
- `.agents/logs/automated_reviews.jsonl`
- Quality scores and recommendations

### 11. Frontend Reviewer Agent
**Purpose**: Reviews frontend code and UI quality

**Location**: `tools/frontend_reviewer_agent.py`

**Responsibilities**:
- Check HTML/CSS/JavaScript quality
- Verify UI functionality
- Test user interactions
- Ensure responsive design

**Outputs**:
- Frontend quality reports
- UI/UX improvement suggestions

### 12. Scientific Reviewer Agent
**Purpose**: Validates scientific accuracy

**Location**: `tools/scientific_reviewer_agent.py`

**Responsibilities**:
- Verify fire behavior physics
- Validate against published research
- Check FBP compliance
- Review fuel model accuracy

**Outputs**:
- Scientific validation reports
- Physics accuracy assessments

## Development Team Agents

### 1. Backend Cleanup Agent
**Purpose**: Maintains Python code quality

**Responsibilities**:
- Remove unused imports
- Fix PEP8 violations
- Add type hints
- Improve error handling

**DNA Location**: `.agents/development_team/dna/backend-developer-agent/`

### 2. Frontend Cleanup Agent
**Purpose**: Maintains frontend code quality

**Responsibilities**:
- Clean HTML/CSS/JavaScript
- Improve accessibility
- Optimize performance
- Fix console errors

**DNA Location**: `.agents/development_team/dna/ui-engineer-agent/`

### 3. Refactoring Agent
**Purpose**: Improves code architecture

**Responsibilities**:
- Identify large files for splitting
- Extract duplicate code
- Reduce complexity
- Apply design patterns

**DNA Location**: `.agents/development_team/dna/data-engineer-agent/`

### 4. Documentation Agent
**Purpose**: Maintains documentation quality

**Responsibilities**:
- Add docstrings
- Update README files
- Document APIs
- Create architecture guides

**DNA Location**: `.agents/development_team/dna/qa-engineer-agent/`

## Agent Communication

### Feedback Broker
**Location**: `tools/feedback_broker.py`

Facilitates inter-agent communication:
- Publish/subscribe message passing
- Shared state management
- Coordination between agents
- Event-driven notifications

### Communication Patterns

1. **Direct Communication**: Agent A → Agent B
   ```python
   broker = FeedbackBroker()
   broker.publish("fire_model", {"status": "complete", "output": "path"})
   ```

2. **Broadcast**: Agent A → All Agents
   ```python
   broker.broadcast({"event": "evolution_triggered"})
   ```

3. **Request/Response**: Agent A ↔ Agent B
   ```python
   response = broker.request("validation_agent", {"action": "validate"})
   ```

## DNA System

### Agent Genome Structure

Each agent has a "genome" that evolves over time:

```json
{
  "agent": "agent-name",
  "session": 0,
  "skills": ["skill1", "skill2"],
  "patterns": ["pattern1", "pattern2"],
  "experience": {
    "successes": [],
    "failures": [],
    "learnings": []
  },
  "created": "ISO timestamp",
  "last_updated": "ISO timestamp"
}
```

**Location**: `.agents/development_team/dna/{agent-name}/genome.json`

### Evolution Process

1. **Pre-Evolution**: Agents prepare for evolution
   - Hook: `.agents/hooks/pre_validation_hook.sh`

2. **Validation**: Agents validate current performance
   - Validation agent compares outputs to ground truth

3. **Post-Evolution**: Agents sync and update DNA
   - Hook: `.agents/hooks/post_evolution_hook.sh`
   - Sync hook: `.agents/hooks/dev_sync_hook.sh`

### DNA Evolution Triggers

- Performance improvement detected
- New patterns learned
- Successful problem resolution
- User feedback incorporated

## Workflow

### Standard Evolution Cycle

```bash
./run_all.sh
```

**Steps**:
1. Fire model agent runs simulation
2. Validation agent compares to ground truth
3. Memory agent records results
4. Mentor agent provides feedback
5. Anomaly agent checks for issues
6. Dashboard agent updates visualizations
7. Review agents analyze outputs
8. Snapshot agent archives state
9. DNA updated with learnings
10. Reports generated

### Development Cleanup Cycle

```bash
bash cleanup.sh
# or
bash .agents/dev-team-controller.sh
```

**Steps**:
1. Backend cleanup agent runs
2. Frontend cleanup agent runs
3. Refactoring agent analyzes
4. Documentation agent assesses
5. Reports generated
6. DNA updated

## Directory Structure

```
.agents/
├── dna/                          # Core agent DNA
│   ├── commit-dna.py            # DNA versioning
│   └── self_audit.py            # Self-assessment
├── development_team/             # Development agents
│   ├── dna/                     # Development agent DNA
│   │   ├── backend-developer-agent/
│   │   ├── ui-engineer-agent/
│   │   ├── data-engineer-agent/
│   │   └── qa-engineer-agent/
│   ├── tasks/                   # Agent task definitions
│   ├── reports/                 # Agent outputs
│   └── status/                  # Current agent status
├── hooks/                        # Lifecycle hooks
│   ├── pre_validation_hook.sh
│   ├── post_evolution_hook.sh
│   ├── dev_sync_hook.sh
│   └── post_visual_hook.sh
├── logs/                         # Agent logs
│   ├── validation_history.jsonl
│   ├── mentor_feedback.log
│   └── automated_reviews.jsonl
├── memory/                       # Persistent memory
├── review/                       # Review history
│   └── history/                 # Archived states
├── snapshots/                    # Agent snapshots
└── state/                        # Current state
```

## Configuration

### Agent Tasks
Tasks are defined in JSON format:

```json
{
  "agent": "agent-name",
  "tasks": [
    {
      "task_id": "unique-id",
      "priority": "high|medium|low",
      "status": "pending|in-progress|blocked|complete",
      "objective": "What to do",
      "scope": {
        "files": [],
        "directories": [],
        "exclusions": []
      },
      "success_criteria": []
    }
  ]
}
```

**Location**: `.agents/development_team/tasks/{agent}-tasks.json`

### Agent Status
Current status tracked in JSON:

```json
{
  "agent": "agent-name",
  "status": "completed|in_progress|blocked",
  "tasks_completed": [],
  "issues_found": [],
  "timestamp": "ISO timestamp"
}
```

**Location**: `.agents/development_team/status/{agent}-status.json`

## Monitoring

### Developer Dashboard
**Location**: `tools/developer_dashboard.py`

**Access**: http://localhost:8085

**Features**:
- Real-time agent DNA status
- Evolution metrics visualization
- Mentor feedback display
- Historical trends

**Start**:
```bash
python3 tools/developer_dashboard.py
```

### Command-Line Monitoring

```bash
# View agent status
cat .agents/development_team/status/*.json | jq

# View DNA
cat .agents/development_team/dna/*/genome.json | jq

# View reports
cat .agents/development_team/reports/*.json | jq

# View logs
tail -f .agents/logs/mentor_feedback.log
```

## Best Practices

### Adding New Agents

1. Create agent script in `tools/`
2. Define agent prompt in `.agents/`
3. Create task definition in `.agents/development_team/tasks/`
4. Initialize DNA in `.agents/development_team/dna/`
5. Add to controller in `.agents/dev-team-controller.sh`

### Agent Development Guidelines

- **Single Responsibility**: Each agent has one clear purpose
- **Stateless Operations**: Agents don't maintain state between runs
- **DNA Updates**: Always update genome after learning
- **Error Handling**: Gracefully handle failures and report them
- **Logging**: Log all significant decisions and actions
- **Testing**: Test agents independently before integration

### Performance Optimization

- Run agents in parallel when possible
- Cache expensive computations
- Use efficient file I/O
- Minimize redundant validations
- Profile and optimize bottlenecks

## Troubleshooting

### Agent Not Running
1. Check agent prompt exists in `.agents/`
2. Verify task file in `.agents/development_team/tasks/`
3. Check permissions on executable files
4. Review logs in `.agents/logs/`

### Poor Performance
1. Check validation metrics in `validation_history.jsonl`
2. Review mentor feedback log
3. Examine anomaly reports
4. Compare with previous snapshots

### DNA Not Updating
1. Verify post-evolution hook runs
2. Check dev sync hook executes
3. Ensure genome.json is writable
4. Review DNA update logic

## Future Enhancements

### Planned Features
- **Multi-Agent Collaboration**: Coordinated task execution
- **Self-Healing**: Automatic recovery from failures
- **Adaptive Learning Rates**: Dynamic evolution speeds
- **Cross-Project Learning**: Share knowledge between projects
- **Natural Language Interface**: Chat with agents

### Research Directions
- Reinforcement learning for agent coordination
- Meta-learning for faster adaptation
- Swarm intelligence patterns
- Emergent behavior from agent interactions

## References

- [Canadian Forest Fire Behavior Prediction System](https://cfs.nrcan.gc.ca/publications?id=10068)
- [Fire Weather Index System](https://cwfis.cfs.nrcan.gc.ca/background/summary/fwi)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)

---

**Last Updated**: October 28, 2025
**Version**: 2.0
**Maintainer**: Development Team Multi-Agent System
