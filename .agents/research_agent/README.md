# Research Agent

Autonomous research capability for gathering and synthesizing external wildfire intelligence.

## Overview

The Research Agent is a sandboxed, auditable system that can autonomously:
- Execute structured research missions
- Search for and analyze external information
- Generate structured findings with source attribution
- Stage outputs for expert review
- Integrate verified knowledge into the simulator's knowledge base

**Design Philosophy**: The research agent operates in isolation from core simulation logic. All outputs are quarantined in `knowledge/unverified/` until manually reviewed and promoted to `knowledge/trusted/`.

## Architecture

```
.agents/research_agent/
├── missions/
│   ├── active/           # Missions ready to execute
│   ├── completed/        # Successfully completed missions
│   └── templates/        # Mission templates
├── runs/                 # Timestamped research run outputs
├── logs/                 # Agent execution logs
├── dna/                  # Agent evolution tracking (if applicable)
└── README.md            # This file

src/agents/research/
├── __init__.py
├── schemas.py            # JSON schemas for all data structures
├── mission_executor.py   # AutoGPT-style research orchestration
├── sanitizer.py          # Output cleaning and validation
└── knowledge_manager.py  # Artifact staging and promotion

knowledge/
├── unverified/           # Quarantine zone for new research
└── trusted/              # Reviewed and approved knowledge
```

## Mission Lifecycle

```
1. Mission Creation
   └─> missions/active/<mission_id>.json

2. Execution
   └─> runs/<timestamp>_<mission_id>/
       ├── raw_findings.json
       ├── metadata.json
       ├── reasoning_trace.json
       └── search_log.json

3. Sanitization
   └─> knowledge/unverified/<mission_id>/
       ├── artifact.json
       ├── summary.md
       └── sources.json

4. Review & Promotion
   └─> knowledge/trusted/<mission_id>/
       └── (same structure, trust_level: "TRUSTED")

5. Consumption
   └─> Internal agents can safely read from knowledge/trusted/
```

## Quick Start

### 1. Create a Mission

Create a JSON file in `missions/active/`:

```json
{
  "mission_id": "ember_transport_research",
  "goal": "Research ember transport distances in eucalyptus forests during extreme fire weather",
  "constraints": {
    "max_sources": 10,
    "max_search_queries": 5,
    "time_limit_minutes": 15
  },
  "deliverables": ["summary", "source_list", "key_findings"],
  "created_at": "2025-02-28T14:30:00Z",
  "priority": "high",
  "context": {
    "background": "Needed for improving spotting model accuracy in Australian fuel types",
    "keywords": ["ember transport", "eucalyptus", "spotting", "extreme fire weather"]
  }
}
```

### 2. Execute the Mission

```bash
python tools/research_orchestrator.py execute ember_transport_research
```

This will:
- Run the research loop
- Generate findings
- Sanitize outputs
- Stage to `knowledge/unverified/`

### 3. Review the Results

```bash
python tools/research_reviewer.py review ember_transport_research
```

### 4. Promote to Trusted (if valid)

```bash
python tools/research_reviewer.py promote ember_transport_research \
  --reviewer "fire-behavior-expert" \
  --notes "Validated against Alexander 2013 ember transport model"
```

## CLI Tools

### Research Orchestrator

Manages mission execution:

```bash
# List active missions
python tools/research_orchestrator.py list-active

# Execute a mission
python tools/research_orchestrator.py execute <mission_id>

# Check run status
python tools/research_orchestrator.py status <run_id>

# Show statistics
python tools/research_orchestrator.py stats
```

### Research Reviewer

Manages artifact review and promotion:

```bash
# List unverified artifacts
python tools/research_reviewer.py list

# Review an artifact
python tools/research_reviewer.py review <mission_id>

# Promote to trusted
python tools/research_reviewer.py promote <mission_id> --reviewer <name>

# Delete an artifact
python tools/research_reviewer.py delete <mission_id>
```

## Mission Schema

All missions must conform to the schema defined in `src/agents/research/schemas.py`:

**Required Fields**:
- `mission_id`: Unique identifier (lowercase, alphanumeric, underscores, hyphens)
- `goal`: Clear research objective (10-500 characters)
- `constraints`: Limits on searches, sources, time
- `deliverables`: Array of required outputs
- `created_at`: ISO 8601 timestamp

**Optional Fields**:
- `priority`: "low" | "medium" | "high" | "urgent"
- `context`: Background, related missions, keywords

## Safety & Isolation

The research agent is designed with multiple safety layers:

### 1. **Sandboxing**
- Execution restricted to `.agents/research_agent/` working directory
- No write access to `src/`, `outputs/`, or core simulation code

### 2. **Sanitization**
All outputs pass through sanitization that:
- Removes executable code blocks
- Validates source URLs
- Enforces size limits (1MB max per artifact)
- Strips potential command injection vectors
- Marks all outputs as "UNVERIFIED"

### 3. **Trust Boundaries**
- Outputs staged to `knowledge/unverified/` by default
- Core agents **only** read from `knowledge/trusted/`
- Manual review required for promotion

### 4. **Audit Trail**
Every operation logged to:
- `logs/research_promotions.log` (promotions/deletions)
- `.agents/research_agent/logs/` (execution logs)
- `runs/<run_id>/` (complete execution trace)

## Milestone 1 Status

**Current Implementation**: Placeholder research loop

The current implementation simulates research operations to validate the architecture. It:
- ✅ Reads mission specifications
- ✅ Creates timestamped run directories
- ✅ Generates placeholder findings
- ✅ Produces complete audit trails
- ✅ Sanitizes and validates outputs
- ✅ Stages to knowledge/unverified/

**Milestone 2**: Real AutoGPT implementation will add:
- Real web search integration
- LLM-based reasoning and synthesis
- Source validation and fact-checking
- Advanced sanitization

## Integration with Internal Agents

Internal domain agents can consume trusted research by:

```python
from pathlib import Path
import json

def load_trusted_research(mission_id: str) -> dict:
    """Load a trusted research artifact."""
    artifact_path = Path("knowledge/trusted") / mission_id / "artifact.json"

    if not artifact_path.exists():
        return None

    with open(artifact_path, 'r') as f:
        artifact = json.load(f)

    # Verify trust level
    if artifact.get("trust_level") != "TRUSTED":
        raise ValueError(f"Artifact {mission_id} is not trusted")

    return artifact
```

**Important**: Internal agents should **never** read from `knowledge/unverified/`.

## Examples

See `missions/templates/` for example mission specifications.

## Troubleshooting

**Mission execution fails**:
- Check mission JSON syntax: `python -m json.tool missions/active/<mission>.json`
- Verify all required fields present
- Check logs in `.agents/research_agent/logs/`

**Sanitization errors**:
- Review warnings in staged artifact's `metadata.warnings`
- Check run directory for `error.log`

**Promotion fails**:
- Ensure artifact exists in `knowledge/unverified/`
- Check not already in `knowledge/trusted/`

## Future Enhancements

- [ ] Real web search integration (Milestone 2)
- [ ] LLM-based reasoning (Milestone 2)
- [ ] Multi-agent collaboration (research + verification)
- [ ] Automated literature citation parsing
- [ ] Integration with arXiv, Google Scholar APIs
- [ ] Confidence scoring based on source quality
- [ ] Automatic update notifications for stale research

## Security Notes

**Do NOT**:
- Execute research on untrusted/malicious mission specifications
- Manually edit files in `runs/` directories (immutable audit trail)
- Promote artifacts without thorough review
- Allow internal agents to read from `unverified/`

**Do**:
- Review all sanitization warnings before promotion
- Validate source URLs and citations
- Document your review process in promotion notes
- Regularly audit `logs/research_promotions.log`

## License

Part of wildfire-simulator-v2. See parent repository for license information.
