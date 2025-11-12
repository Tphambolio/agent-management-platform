#!/usr/bin/env python3
"""
Claude Code CLI Report Generator

This script generates scientific reports using Claude Code CLI instead of API calls.
No API credits needed - uses the CLI you're already running!
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_agent_genome(agent_name: str) -> dict:
    """Load agent's genome/training data"""
    dna_dir = Path("/home/rpas/agent-management-platform/.agents/dna")

    dir_name = agent_name.lower().replace(" agent", "").replace(" ", "-") + "-agent"
    genome_path = dna_dir / dir_name / "genome.json"

    if genome_path.exists():
        with open(genome_path, 'r') as f:
            return json.load(f)
    return {}

def generate_report_prompt(agent_name: str, task_title: str, task_description: str, research_data: dict = None) -> str:
    """Generate the prompt for Claude Code to create a scientific report"""

    genome = load_agent_genome(agent_name)
    metadata = genome.get("agent_metadata", {})
    skills = genome.get("skills", {})

    prompt = f"""You are {agent_name}, a specialized AI agent.

# Your Profile
- Training Sessions: {metadata.get('total_sessions', 0)}
- Evolution Stage: {metadata.get('evolution_stage', 'beginner')}
- Specialization: {metadata.get('role', 'general')}

# Your Task
**Title:** {task_title}
**Description:** {task_description}

"""

    if research_data and research_data.get("sources"):
        prompt += "\n# Web Research Findings\n"
        for i, source in enumerate(research_data["sources"][:10], 1):
            prompt += f"\n**Source {i}: {source['title']}**\n"
            prompt += f"URL: {source['url']}\n"
            prompt += f"{source['description']}\n"

    prompt += """

# Your Mission: Generate a SCIENTIFIC RESEARCH REPORT

**CRITICAL REQUIREMENTS:**
- Include at least 2-3 executable Python code blocks
- Show actual numerical results, not placeholders
- Use technical precision and domain expertise
- Format as a scientific journal article

**Required Structure:**

## Abstract
[150-250 words: Problem, methods, key findings, significance]

## 1. Introduction
### 1.1 Background and Motivation
[Scientific context and importance]

### 1.2 Research Question/Objective
[Clear statement of investigation]

## 2. Methodology
### 2.1 Approach
[Describe methods with technical precision]

### 2.2 Implementation
[Include working Python code]

```python
# Real computation based on research
import numpy as np

# YOUR CODE HERE - must be executable
```

## 3. Results
### 3.1 Computational Findings
[Present actual data and calculations]

### 3.2 Analysis
[Interpret results using expertise]

## 4. Discussion
### 4.1 Key Insights
[Connect to broader knowledge]

### 4.2 Implications
[What this means for the field]

## 5. Code Repository
### 5.1 Core Algorithms
[Production-ready code]

```python
def algorithm_name(parameters):
    \"\"\"
    Docstring explaining the method

    Args:
        parameters: Description

    Returns:
        Results with units
    \"\"\"
    # Implementation
    pass
```

## 6. Conclusions
[Summarize findings and future work]

## References
[Cite sources]

Generate this report now using your expertise!
"""

    return prompt

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python generate_report.py <agent_name> <task_title> <task_description>")
        sys.exit(1)

    agent_name = sys.argv[1]
    task_title = sys.argv[2]
    task_description = sys.argv[3]

    prompt = generate_report_prompt(agent_name, task_title, task_description)

    print("=" * 80)
    print("PROMPT FOR CLAUDE CODE CLI:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print("\nNow paste this into Claude Code CLI to generate the report!")
