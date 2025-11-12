"""Agent Manager - Discovers and manages agents"""
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .models import Agent, Task, Report, AgentStatus, TaskStatus, Project
from .config import settings
from .executor import agent_executor


class AgentManager:
    """Manages agent discovery, execution, and state"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.reports: Dict[str, Report] = {}
        self.projects: Dict[str, Project] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}

    async def initialize(self):
        """Initialize the agent manager"""
        await self.discover_agents()
        await self.load_existing_tasks()
        await self.load_projects()

    async def discover_agents(self):
        """Discover all agents from the .agents directory"""
        agents_found = []

        # Discover domain agents
        domain_dir = settings.DOMAIN_AGENTS_DIR
        if domain_dir.exists():
            for agent_file in domain_dir.glob("*.txt"):
                agent = await self._parse_agent_file(agent_file, "domain")
                if agent:
                    agents_found.append(agent)

        # Discover development team agents
        dev_dir = settings.DEV_TEAM_DIR
        if dev_dir.exists():
            for agent_file in dev_dir.glob("*.txt"):
                agent = await self._parse_agent_file(agent_file, "development")
                if agent:
                    agents_found.append(agent)

        # Update agents dictionary
        for agent in agents_found:
            self.agents[agent.id] = agent

        return agents_found

    async def _parse_agent_file(self, file_path: Path, agent_type: str) -> Optional[Agent]:
        """Parse an agent definition file"""
        try:
            content = file_path.read_text()

            # Extract agent info from the file
            name = file_path.stem.replace("-", " ").replace("_", " ").title()
            agent_id = file_path.stem

            # Try to extract description and capabilities
            lines = content.split('\n')
            description = ""
            capabilities = []

            for i, line in enumerate(lines):
                if line.strip().startswith("ROLE:") or line.strip().startswith("Role:"):
                    description = line.split(":", 1)[1].strip()
                elif line.strip().startswith("CAPABILITIES:") or line.strip().startswith("Capabilities:"):
                    # Look for bullet points or list items
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip().startswith(("-", "*", "•")):
                            cap = lines[j].strip().lstrip("-*•").strip()
                            if cap:
                                capabilities.append(cap)

            # If no description found, use first non-empty line
            if not description:
                for line in lines[:5]:
                    if line.strip() and not line.strip().startswith("#"):
                        description = line.strip()
                        break

            # Check for status file
            status = AgentStatus.IDLE
            status_file = settings.STATUS_DIR / f"{agent_id}-status.json"
            if status_file.exists():
                status_data = json.loads(status_file.read_text())
                status = AgentStatus(status_data.get("status", "idle"))

            return Agent(
                id=agent_id,
                name=name,
                type=agent_type,
                description=description or f"{name} agent",
                status=status,
                capabilities=capabilities,
                metadata={
                    "file_path": str(file_path),
                    "discovered_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error parsing agent file {file_path}: {e}")
            return None

    async def list_agents(self, agent_type: Optional[str] = None) -> List[Agent]:
        """List all agents, optionally filtered by type"""
        agents = list(self.agents.values())
        if agent_type:
            agents = [a for a in agents if a.type == agent_type]
        return agents

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get a specific agent by ID"""
        return self.agents.get(agent_id)

    async def create_task(
        self,
        agent_id: str,
        title: str,
        description: str,
        project_id: Optional[str] = None,
        context: Optional[Dict] = None,
        priority: str = "medium"
    ) -> Task:
        """Create a new task for an agent"""
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        task = Task(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            project_id=project_id,
            title=title,
            description=description,
            priority=priority,
            context=context or {}
        )

        self.tasks[task.id] = task

        # Save task to disk
        task_file = settings.TASKS_DIR / f"{task.id}.json"
        task_file.write_text(task.model_dump_json(indent=2))

        return task

    async def execute_task(self, task_id: str) -> Task:
        """Execute a task"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        agent = self.agents.get(task.agent_id)
        if not agent:
            raise ValueError(f"Agent {task.agent_id} not found")

        # Update task and agent status
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        agent.status = AgentStatus.RUNNING
        agent.current_task = task_id

        # Create async task for execution
        async_task = asyncio.create_task(self._execute_agent_task(task, agent))
        self._running_tasks[task_id] = async_task

        return task

    async def _execute_agent_task(self, task: Task, agent: Agent):
        """Execute an agent task using the agent executor"""
        try:
            # Execute the task using the executor
            result = await agent_executor.execute_task(task, agent)

            # Update task with result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result

            # Create a report from the output
            report_content = result.get("output", result)
            report = Report(
                id=str(uuid.uuid4()),
                task_id=task.id,
                agent_id=agent.id,
                title=f"Report: {task.title}",
                content=report_content,
                format="json",
                metadata={
                    "execution_method": result.get("execution_method", "unknown"),
                    "model": result.get("model"),
                    "tokens_used": result.get("tokens_used")
                }
            )
            self.reports[report.id] = report

            # Save report
            report_file = settings.REPORTS_DIR / f"{report.id}.json"
            report_file.write_text(report.model_dump_json(indent=2))

            # Update agent status
            agent.status = AgentStatus.IDLE
            agent.current_task = None
            agent.last_activity = datetime.utcnow()

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            agent.status = AgentStatus.ERROR
            agent.current_task = None

        finally:
            # Save task state
            task_file = settings.TASKS_DIR / f"{task.id}.json"
            task_file.write_text(task.model_dump_json(indent=2))

            # Remove from running tasks
            self._running_tasks.pop(task.id, None)

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)

    async def list_tasks(
        self,
        agent_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        project_id: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filters"""
        tasks = list(self.tasks.values())

        if agent_id:
            tasks = [t for t in tasks if t.agent_id == agent_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if project_id:
            tasks = [t for t in tasks if t.project_id == project_id]

        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    async def get_report(self, report_id: str) -> Optional[Report]:
        """Get a report by ID"""
        return self.reports.get(report_id)

    async def list_reports(
        self,
        task_id: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> List[Report]:
        """List reports with optional filters"""
        reports = list(self.reports.values())

        if task_id:
            reports = [r for r in reports if r.task_id == task_id]
        if agent_id:
            reports = [r for r in reports if r.agent_id == agent_id]

        return sorted(reports, key=lambda r: r.created_at, reverse=True)

    async def load_existing_tasks(self):
        """Load existing tasks from disk"""
        if not settings.TASKS_DIR.exists():
            return

        for task_file in settings.TASKS_DIR.glob("*.json"):
            try:
                task_data = json.loads(task_file.read_text())
                task = Task(**task_data)
                self.tasks[task.id] = task
            except Exception as e:
                print(f"Error loading task from {task_file}: {e}")

    async def create_project(
        self,
        name: str,
        description: str,
        repository_path: Optional[str] = None
    ) -> Project:
        """Create a new project"""
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            repository_path=repository_path
        )

        self.projects[project.id] = project

        # Save project
        project_file = settings.PROJECTS_DIR / f"{project.id}.json"
        project_file.write_text(project.model_dump_json(indent=2))

        return project

    async def load_projects(self):
        """Load existing projects from disk"""
        if not settings.PROJECTS_DIR.exists():
            return

        for project_file in settings.PROJECTS_DIR.glob("*.json"):
            try:
                project_data = json.loads(project_file.read_text())
                project = Project(**project_data)
                self.projects[project.id] = project
            except Exception as e:
                print(f"Error loading project from {project_file}: {e}")

    async def list_projects(self) -> List[Project]:
        """List all projects"""
        return list(self.projects.values())

    async def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID"""
        return self.projects.get(project_id)


# Global agent manager instance
agent_manager = AgentManager()
