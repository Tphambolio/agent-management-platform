#!/usr/bin/env python3
"""
Claude Code CLI Task Watcher

This script runs alongside your Agent Management Platform and uses
Claude Code CLI to generate scientific reports. No API costs!

How it works:
1. Watches /app/.agents/pending_tasks/ for new task files
2. Reads task details and agent genome
3. Generates a scientific report using the agent's expertise
4. Saves result to /app/.agents/task_results/
"""

import json
import time
from pathlib import Path
from datetime import datetime
import sys

class ClaudeCodeTaskWatcher:
    def __init__(self):
        self.tasks_dir = Path("/home/rpas/agent-management-platform/.agents/pending_tasks")
        self.results_dir = Path("/home/rpas/agent-management-platform/.agents/task_results")
        self.dna_dir = Path("/home/rpas/agent-management-platform/.agents/dna")

        # Create directories
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        print("🤖 Claude Code CLI Task Watcher Started")
        print(f"   Watching: {self.tasks_dir}")
        print(f"   Results: {self.results_dir}")
        print(f"   DNA: {self.dna_dir}")

    def load_agent_genome(self, agent_name: str) -> dict:
        """Load agent's genome/training data"""
        dir_name = agent_name.lower().replace(" agent", "").replace(" ", "-") + "-agent"
        genome_path = self.dna_dir / dir_name / "genome.json"

        if genome_path.exists():
            with open(genome_path, 'r') as f:
                return json.load(f)
        return {}

    def generate_prompt(self, task: dict) -> str:
        """Generate prompt for Claude Code CLI"""

        genome = self.load_agent_genome(task['agent_name'])
        metadata = genome.get("agent_metadata", {})
        skills = genome.get("skills", {})
        experience = genome.get("experience_bank", {})

        prompt = f"""You are {task['agent_name']}, a specialized AI agent with {metadata.get('total_sessions', 0)} training sessions.

# Task Assignment
**Title:** {task['task_title']}
**Description:** {task['task_description']}

# Your Expertise
"""

        # Add domain skills
        domain_skills = skills.get("domain", {})
        if domain_skills:
            prompt += "\n## Domain Skills\n"
            for skill_name, skill_data in list(domain_skills.items())[:5]:
                if isinstance(skill_data, dict):
                    prompt += f"- **{skill_name}**: {skill_data.get('description', '')}\n"

        # Add patterns known
        patterns = experience.get("patterns_known", [])
        if patterns:
            prompt += f"\n## Known Patterns ({len(patterns)} total)\n"
            for pattern in patterns[:5]:
                name = pattern.get("name", "")
                desc = pattern.get("description", "")
                prompt += f"- **{name}**: {desc}\n"

        # Add research data if available
        if task.get('research_data') and task['research_data'].get('sources'):
            prompt += "\n# Web Research Findings\n"
            for i, source in enumerate(task['research_data']['sources'][:10], 1):
                prompt += f"\n**Source {i}: {source['title']}**\n"
                prompt += f"URL: {source['url']}\n"
                prompt += f"{source['description']}\n"

        prompt += """

# Your Mission: Generate a SCIENTIFIC RESEARCH REPORT

**CRITICAL REQUIREMENTS:**
1. Include at least 2-3 executable Python code blocks
2. Show actual numerical results, not placeholders
3. Use technical precision and your domain expertise
4. Format as a scientific journal article

**Required Structure:**

## Abstract
[150-250 words: Problem, methods, key findings, significance]

## 1. Introduction
### 1.1 Background and Motivation
### 1.2 Research Question/Objective

## 2. Methodology
### 2.1 Approach
### 2.2 Implementation
```python
# Include working Python code with real calculations
import numpy as np

# YOUR CODE HERE
```

## 3. Results
### 3.1 Computational Findings
[Present actual data and calculations]

### 3.2 Analysis

## 4. Discussion
### 4.1 Key Insights
### 4.2 Implications

## 5. Code Repository
### 5.1 Core Algorithms
```python
def algorithm_name(parameters):
    \"\"\"
    Production-ready code that agents can learn from
    \"\"\"
    pass
```

## 6. Conclusions

## References

**Generate this scientific report now using your specialized training and expertise!**
"""

        return prompt

    def process_task(self, task_file: Path):
        """Process a single task file"""

        try:
            # Load task
            with open(task_file, 'r') as f:
                task = json.load(f)

            task_id = task['task_id']
            print(f"\n📋 Processing task: {task_id}")
            print(f"   Agent: {task['agent_name']}")
            print(f"   Title: {task['task_title']}")

            # Generate prompt
            prompt = self.generate_prompt(task)

            # Save prompt for manual processing
            prompt_file = self.results_dir / f"{task_id}_prompt.txt"
            with open(prompt_file, 'w') as f:
                f.write(prompt)

            print(f"\n💡 PROMPT SAVED TO: {prompt_file}")
            print("\n" + "="*80)
            print("ACTION REQUIRED:")
            print("="*80)
            print(f"1. Copy the prompt from: {prompt_file}")
            print(f"2. Paste it into Claude Code CLI")
            print(f"3. Save the generated report to:")
            print(f"   {self.results_dir}/{task_id}_result.json")
            print("\nFormat of result file:")
            print(json.dumps({
                "task_id": task_id,
                "agent_name": task['agent_name'],
                "status": "success",
                "content": "[YOUR GENERATED REPORT HERE]",
                "completed_at": datetime.utcnow().isoformat(),
                "model": "claude-code-cli"
            }, indent=2))
            print("="*80)

            # Mark task as processed
            processed_file = task_file.with_suffix('.processing')
            task_file.rename(processed_file)

        except Exception as e:
            print(f"❌ Error processing task: {e}")

    def watch(self):
        """Watch for new tasks"""

        print("\n👀 Watching for new tasks... (Press Ctrl+C to stop)")

        try:
            while True:
                # Check for new task files
                task_files = list(self.tasks_dir.glob("*.json"))

                for task_file in task_files:
                    self.process_task(task_file)

                # Sleep
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n\n🛑 Watcher stopped")

if __name__ == "__main__":
    watcher = ClaudeCodeTaskWatcher()
    watcher.watch()
