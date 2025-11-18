"""Agent Executor - Executes agent tasks using LLMs or scripts"""
import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .models import Agent, Task, Report
from .config import settings


class AgentExecutor:
    """Executes agent tasks"""

    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.use_llm = self.anthropic_api_key is not None

    async def execute_task(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Execute a task using the appropriate method"""

        # Load agent instructions
        agent_file = Path(agent.metadata.get("file_path", ""))
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent file not found: {agent_file}")

        agent_instructions = agent_file.read_text()

        # Prepare context
        context = self._prepare_context(task, agent, agent_instructions)

        # Execute based on availability
        if self.use_llm:
            result = await self._execute_with_llm(context, task, agent)
        else:
            result = await self._execute_mock(context, task, agent)

        return result

    def _prepare_context(self, task: Task, agent: Agent, agent_instructions: str) -> Dict[str, Any]:
        """Prepare execution context"""
        context = {
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type,
                "instructions": agent_instructions,
                "capabilities": agent.capabilities
            },
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority.value,
                "context": task.context
            },
            "project": {},
            "execution_time": datetime.utcnow().isoformat()
        }

        # Add project context if available
        if task.project_id:
            # Load project info
            project_file = settings.PROJECTS_DIR / f"{task.project_id}.json"
            if project_file.exists():
                project_data = json.loads(project_file.read_text())
                context["project"] = project_data

        return context

    async def _execute_with_llm(self, context: Dict[str, Any], task: Task, agent: Agent) -> Dict[str, Any]:
        """Execute task using LLM (Claude)"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.anthropic_api_key)

            # Build the prompt
            prompt = self._build_llm_prompt(context)

            # Call Claude
            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            response_text = message.content[0].text

            # Parse response if it's JSON
            try:
                result_data = json.loads(response_text)
            except json.JSONDecodeError:
                result_data = {
                    "output": response_text,
                    "format": "text"
                }

            return {
                "status": "success",
                "output": result_data,
                "execution_method": "llm",
                "model": "claude-sonnet-4-5",
                "tokens_used": message.usage.input_tokens + message.usage.output_tokens
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "execution_method": "llm"
            }

    async def _execute_mock(self, context: Dict[str, Any], task: Task, agent: Agent) -> Dict[str, Any]:
        """Execute task with mock data (for testing without API key)"""
        # Simulate some processing time
        await asyncio.sleep(2)

        # Generate mock report based on agent type
        if agent.type == "development":
            output = self._generate_development_report(task, agent)
        elif agent.type == "domain":
            output = self._generate_domain_report(task, agent)
        else:
            output = self._generate_generic_report(task, agent)

        return {
            "status": "success",
            "output": output,
            "execution_method": "mock",
            "note": "This is mock data. Set ANTHROPIC_API_KEY to use real LLM execution."
        }

    def _build_llm_prompt(self, context: Dict[str, Any]) -> str:
        """Build the prompt for the LLM"""
        agent = context["agent"]
        task = context["task"]
        project = context.get("project", {})

        prompt = f"""You are {agent['name']}, an AI agent with the following role and capabilities:

AGENT INSTRUCTIONS:
{agent['instructions']}

CAPABILITIES:
{', '.join(agent['capabilities']) if agent['capabilities'] else 'General purpose'}

YOUR TASK:
Title: {task['title']}
Description: {task['description']}
Priority: {task['priority']}

"""

        if task.get("context"):
            prompt += f"""TASK CONTEXT:
{json.dumps(task['context'], indent=2)}

"""

        if project:
            prompt += f"""PROJECT INFORMATION:
Name: {project.get('name', 'N/A')}
Description: {project.get('description', 'N/A')}
Repository: {project.get('repository_path', 'N/A')}

"""

        prompt += """Please complete the task according to your role and capabilities.

Provide your response in the following JSON format:
{
  "summary": "Brief summary of what you did",
  "findings": ["Finding 1", "Finding 2", ...],
  "recommendations": ["Recommendation 1", "Recommendation 2", ...],
  "details": {
    "any": "additional",
    "structured": "data"
  },
  "status": "completed"
}

If you cannot complete the task or need additional information, explain why in the JSON response.
"""

        return prompt

    def _generate_development_report(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Generate mock development team report"""
        return {
            "summary": f"Completed {task.title} for {agent.name}",
            "findings": [
                "Code structure follows best practices",
                "Found 3 minor optimization opportunities",
                "Documentation is comprehensive"
            ],
            "recommendations": [
                "Consider adding type hints to improve code clarity",
                "Implement caching for frequently accessed data",
                "Add more unit tests for edge cases"
            ],
            "metrics": {
                "files_analyzed": 12,
                "issues_found": 3,
                "severity": "low"
            },
            "status": "completed",
            "execution_note": "Mock execution - for demonstration purposes"
        }

    def _generate_domain_report(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Generate mock domain agent report"""
        return {
            "summary": f"Domain analysis completed for {task.title}",
            "findings": [
                "Domain model is well-structured",
                "Business logic properly separated from presentation",
                "Data validation rules are comprehensive"
            ],
            "recommendations": [
                "Consider implementing domain events for better decoupling",
                "Add integration tests for critical workflows",
                "Document business rules more explicitly"
            ],
            "domain_insights": {
                "entities": 8,
                "aggregates": 3,
                "value_objects": 12
            },
            "status": "completed",
            "execution_note": "Mock execution - for demonstration purposes"
        }

    def _generate_generic_report(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Generate mock generic report"""
        return {
            "summary": f"Task '{task.title}' analyzed by {agent.name}",
            "findings": [
                "Task requirements are clear",
                "No blocking issues identified",
                "All prerequisites are met"
            ],
            "recommendations": [
                "Proceed with implementation",
                "Monitor progress regularly",
                "Document decisions and rationale"
            ],
            "status": "completed",
            "execution_note": "Mock execution - for demonstration purposes"
        }


# Global executor instance
agent_executor = AgentExecutor()
