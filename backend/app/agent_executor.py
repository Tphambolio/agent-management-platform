"""Agent Executor - Integrates with existing file-based agent system"""
import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import uuid

from .database import get_db
from .models import Agent, Task, Report, AgentStatus, TaskStatus


class AgentExecutor:
    """
    Executes agents using the existing wildfire-simulator agent infrastructure.

    This integrates with:
    - Agent prompts in .agents/*.txt
    - Task files in .agents/tasks/*.json
    - Status files in .agents/status/*.json
    - Report files in .agents/reports/*.json
    """

    def __init__(self, agents_dir: str = "/home/rpas/wildfire-simulator-v2/.agents"):
        self.agents_dir = Path(agents_dir)
        self.running_tasks: Dict[str, asyncio.Task] = {}

    def discover_agents(self) -> list[Dict[str, Any]]:
        """
        Discover agents from the .agents directory by reading prompt files.
        Returns a list of agent definitions.
        """
        agents = []

        # Search for agent prompt files
        prompt_files = [
            self.agents_dir / "domain_agents",
            self.agents_dir / "development_team",
            self.agents_dir,
        ]

        discovered = []
        for search_dir in prompt_files:
            if search_dir.exists():
                for txt_file in search_dir.glob("*.txt"):
                    if "agent" in txt_file.stem.lower():
                        discovered.append(txt_file)

        # Parse agent info from prompt files
        for prompt_file in discovered:
            agent_name = prompt_file.stem

            # Read first few lines to extract specialization
            try:
                with open(prompt_file, 'r') as f:
                    first_line = f.readline().strip()
                    specialization = first_line.replace("You are the", "").replace("Agent", "").strip()

                    # Determine agent type
                    agent_type = "development" if "development_team" in str(prompt_file) else "domain"
                    if "orchestrator" in agent_name or "pm-" in agent_name:
                        agent_type = "coordination"

                    agents.append({
                        "name": agent_name,
                        "type": agent_type,
                        "specialization": specialization or agent_name.replace("-", " ").title(),
                        "prompt_file": str(prompt_file),
                        "capabilities": self._extract_capabilities(f),
                    })
            except Exception as e:
                print(f"Warning: Could not parse {prompt_file}: {e}")

        return agents

    def _extract_capabilities(self, file_handle) -> list[str]:
        """Extract capabilities from agent prompt file"""
        capabilities = []
        content = file_handle.read()

        # Look for common capability indicators
        if "RESPONSIBILITIES" in content or "YOUR RESPONSIBILITIES" in content:
            lines = content.split("\n")
            in_responsibilities = False
            for line in lines:
                if "RESPONSIBILITIES" in line:
                    in_responsibilities = True
                    continue
                if in_responsibilities:
                    if line.startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                        capability = line.lstrip("0123456789.-* ").strip()
                        if capability:
                            capabilities.append(capability)
                    elif line.strip() and not line[0].isdigit() and line[0] not in "-*":
                        break

        return capabilities[:5]  # Limit to 5 main capabilities

    async def execute_task(self, task_id: str) -> None:
        """Execute a task asynchronously"""
        try:
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    raise ValueError(f"Task {task_id} not found")

                agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
                if not agent:
                    raise ValueError(f"Agent {task.agent_id} not found")

                # Create task file for agent
                task_file = await self._create_task_file(agent, task)

                # Execute agent using existing infrastructure
                result = await self._run_agent(agent, task)

                # Parse results from report file
                report_data = await self._read_agent_report(agent, task)

                # Update task with results
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result

                # Create report in database
                if report_data:
                    report = Report(
                        id=str(uuid.uuid4()),
                        task_id=task_id,
                        agent_id=agent.id,
                        project_id=task.project_id,
                        title=report_data.get("title", f"{agent.name} - {task.title}"),
                        content=report_data.get("content", json.dumps(report_data, indent=2)),
                        format=report_data.get("format", "json"),
                        summary=report_data.get("summary", ""),
                        tags=report_data.get("tags", [agent.name, task.project_id])
                    )
                    db.add(report)

                # Update agent status
                agent.status = AgentStatus.IDLE
                agent.last_active = datetime.utcnow()

                db.commit()

        except Exception as e:
            # Mark task as failed
            with get_db() as db:
                task = db.query(Task).filter(Task.id == task_id).first()
                if task:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.utcnow()

                    agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
                    if agent:
                        agent.status = AgentStatus.ERROR

                    db.commit()

            print(f"Error executing task {task_id}: {e}")
        finally:
            # Clean up
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

    async def _create_task_file(self, agent: Agent, task: Task) -> Path:
        """Create task file in .agents/tasks/ directory"""
        tasks_dir = self.agents_dir / "tasks"
        tasks_dir.mkdir(exist_ok=True)

        task_file = tasks_dir / f"{agent.name}-tasks.json"

        task_data = {
            "task_id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "context": task.context,
            "created_at": task.created_at.isoformat() if task.created_at else None
        }

        # Append to existing tasks or create new file
        existing_tasks = []
        if task_file.exists():
            with open(task_file, 'r') as f:
                try:
                    existing_tasks = json.load(f)
                    if not isinstance(existing_tasks, list):
                        existing_tasks = [existing_tasks]
                except:
                    existing_tasks = []

        existing_tasks.append(task_data)

        with open(task_file, 'w') as f:
            json.dump(existing_tasks, f, indent=2)

        return task_file

    async def _run_agent(self, agent: Agent, task: Task) -> Dict[str, Any]:
        """Run agent using Claude CLI or existing shell scripts"""

        # Option 1: Use existing shell script if available
        script_path = self.agents_dir / f"run-{agent.name}.sh"
        if script_path.exists():
            process = await asyncio.create_subprocess_exec(
                str(script_path),
                cwd=str(self.agents_dir.parent),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            return {
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "return_code": process.returncode
            }

        # Option 2: Run agent prompt directly
        prompt_file = Path(agent.prompt_file)
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompt = f.read()

            # Inject task information into prompt
            task_context = f"""

ASSIGNED TASK:
--------------
Title: {task.title}
Description: {task.description}
Project: {task.project_id}
Priority: {task.priority}

Additional Context:
{json.dumps(task.context, indent=2)}

Please complete this task and write your report to:
- .agents/reports/{agent.name}-report.json
- .agents/status/{agent.name}-status.json
"""
            full_prompt = prompt + task_context

            # For now, we'll write this to a temporary file
            # In production, you'd invoke Claude API or CLI here
            temp_prompt = self.agents_dir / f"temp-{task.id}.txt"
            with open(temp_prompt, 'w') as f:
                f.write(full_prompt)

            return {
                "prompt_file": str(temp_prompt),
                "note": "Agent prompt prepared. In production, this would invoke Claude API."
            }

        raise ValueError(f"No execution method found for agent {agent.name}")

    async def _read_agent_report(self, agent: Agent, task: Task) -> Optional[Dict[str, Any]]:
        """Read agent report from file system"""
        report_paths = [
            self.agents_dir / "reports" / f"{agent.name}-report.json",
            self.agents_dir / "development_team" / "reports" / f"{agent.name}-report.json",
            self.agents_dir / "domain_agents" / "reports" / f"{agent.name}-report.json",
        ]

        for report_path in report_paths:
            if report_path.exists():
                try:
                    with open(report_path, 'r') as f:
                        data = json.load(f)

                        # If it's a list, get the most recent report
                        if isinstance(data, list) and data:
                            data = data[-1]

                        return data
                except Exception as e:
                    print(f"Warning: Could not read report {report_path}: {e}")

        return None

    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Read agent status from file system"""
        status_paths = [
            self.agents_dir / "status" / f"{agent_name}-status.json",
            self.agents_dir / "development_team" / "status" / f"{agent_name}-status.json",
        ]

        for status_path in status_paths:
            if status_path.exists():
                try:
                    with open(status_path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Warning: Could not read status {status_path}: {e}")

        return None

    def sync_agents_to_db(self) -> None:
        """Sync discovered agents from filesystem to database"""
        discovered_agents = self.discover_agents()

        with get_db() as db:
            for agent_data in discovered_agents:
                # Check if agent already exists
                existing = db.query(Agent).filter(Agent.name == agent_data["name"]).first()

                if not existing:
                    # Create new agent
                    agent = Agent(
                        id=str(uuid.uuid4()),
                        name=agent_data["name"],
                        type=agent_data["type"],
                        specialization=agent_data["specialization"],
                        capabilities=agent_data["capabilities"],
                        prompt_file=agent_data["prompt_file"],
                        status=AgentStatus.IDLE
                    )
                    db.add(agent)
                else:
                    # Update existing agent
                    existing.prompt_file = agent_data["prompt_file"]
                    existing.capabilities = agent_data["capabilities"]
                    existing.specialization = agent_data["specialization"]

            db.commit()
            print(f"Synced {len(discovered_agents)} agents to database")
