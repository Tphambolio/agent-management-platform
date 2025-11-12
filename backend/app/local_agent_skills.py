"""Local Agent Skills System - Uses file-based communication instead of API"""
import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

class LocalAgentSkillsSystem:
    """Manages agent genome data and generates reports without API calls"""

    def __init__(self):
        self.dna_directory = Path("/app/.agents/dna")
        self.tasks_directory = Path("/app/.agents/pending_tasks")
        self.results_directory = Path("/app/.agents/task_results")

        # Create directories
        self.tasks_directory.mkdir(parents=True, exist_ok=True)
        self.results_directory.mkdir(parents=True, exist_ok=True)

        print("✅ Local Agent Skills System initialized (using Claude Code CLI)")

    def load_agent_genome(self, agent_name: str) -> Optional[Dict]:
        """Load agent genome from DNA directory"""

        # Convert agent name to directory name
        dir_name = agent_name.lower()\
            .replace(" agent", "")\
            .replace(" ", "-") + "-agent"

        genome_path = self.dna_directory / dir_name / "genome.json"

        if not genome_path.exists():
            print(f"⚠️  No genome found for {agent_name} at {genome_path}")
            return None

        try:
            with open(genome_path, 'r') as f:
                genome = json.load(f)
                print(f"✅ Loaded genome for {agent_name}")
                return genome
        except Exception as e:
            print(f"❌ Error loading genome: {e}")
            return None

    def create_task_request(
        self,
        task_id: str,
        agent_name: str,
        task_title: str,
        task_description: str,
        research_data: Optional[Dict] = None
    ) -> str:
        """
        Create a task request file for Claude Code CLI to process

        Returns: path to task request file
        """

        genome = self.load_agent_genome(agent_name)

        task_request = {
            "task_id": task_id,
            "agent_name": agent_name,
            "task_title": task_title,
            "task_description": task_description,
            "research_data": research_data,
            "genome": genome,
            "created_at": datetime.utcnow().isoformat(),
            "instructions": """
Generate a SCIENTIFIC RESEARCH REPORT with the following requirements:

1. **Format**: Scientific journal article
2. **Code**: Include at least 2-3 executable Python code blocks
3. **Results**: Show actual numerical results, not placeholders
4. **Structure**:
   - Abstract (150-250 words)
   - Introduction with Background and Research Question
   - Methodology with Implementation and working code
   - Results with Computational Findings
   - Discussion with Key Insights
   - Code Repository with production-ready algorithms
   - Conclusions

Use the agent's genome (skills, patterns, techniques) to inform the report.
Include the research data if provided.
All code must be executable and well-documented.
"""
        }

        task_file = self.tasks_directory / f"{task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task_request, f, indent=2)

        print(f"📝 Created task request: {task_file}")
        return str(task_file)

    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Check if task result is available"""

        result_file = self.results_directory / f"{task_id}_result.json"

        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)

        return None

    def save_task_result(
        self,
        task_id: str,
        report_content: str,
        agent_name: str
    ) -> Dict:
        """Save a task result (for testing/manual generation)"""

        result = {
            "task_id": task_id,
            "agent_name": agent_name,
            "status": "success",
            "content": report_content,
            "completed_at": datetime.utcnow().isoformat(),
            "model": "claude-code-cli"
        }

        result_file = self.results_directory / f"{task_id}_result.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)

        return result

    async def execute_task_with_skills(
        self,
        agent_name: str,
        task_title: str,
        task_description: str,
        research_data: Optional[Dict] = None
    ) -> Dict:
        """
        Create task request for Claude Code CLI to process

        In production, Claude Code CLI would monitor the tasks directory
        and generate reports automatically.

        For now, returns instructions for manual processing.
        """

        task_id = f"task_{datetime.utcnow().timestamp()}"

        task_file = self.create_task_request(
            task_id=task_id,
            agent_name=agent_name,
            task_title=task_title,
            task_description=task_description,
            research_data=research_data
        )

        # Check if result already exists (for testing)
        result = self.get_task_result(task_id)
        if result:
            return result

        # Return pending status
        return {
            "status": "pending_cli_generation",
            "message": f"Task created at {task_file}. Waiting for Claude Code CLI to generate report.",
            "task_id": task_id,
            "task_file": task_file
        }

# Global instance
local_agent_skills_system = LocalAgentSkillsSystem()
