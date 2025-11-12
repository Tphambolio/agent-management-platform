"""MCP Server for Agent Management Platform"""
import asyncio
import json
from typing import Any, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    PromptMessage,
    GetPromptResult
)

from .agent_manager import agent_manager
from .models import TaskPriority


# Create MCP server instance
app = Server("agent-management-platform")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="list_agents",
            description="List all available agents in the workforce. Optionally filter by agent type (domain, development, analysis).",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_type": {
                        "type": "string",
                        "description": "Filter by agent type: domain, development, analysis",
                        "enum": ["domain", "development", "analysis"]
                    }
                }
            }
        ),
        Tool(
            name="get_agent_status",
            description="Get detailed status and information about a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The unique identifier of the agent"
                    }
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="assign_task",
            description="Assign a new task to an agent. The task will be queued for execution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The unique identifier of the agent to assign the task to"
                    },
                    "title": {
                        "type": "string",
                        "description": "A short, descriptive title for the task"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of what the agent should do"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project ID if this task is part of a specific project"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Task priority level",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context data for the task (file paths, parameters, etc.)"
                    }
                },
                "required": ["agent_id", "title", "description"]
            }
        ),
        Tool(
            name="execute_task",
            description="Start execution of a pending task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique identifier of the task to execute"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="get_task_status",
            description="Get the current status and details of a specific task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique identifier of the task"
                    }
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks with optional filters for agent, status, or project",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Filter by agent ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by task status",
                        "enum": ["pending", "running", "completed", "failed", "cancelled"]
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Filter by project ID"
                    }
                }
            }
        ),
        Tool(
            name="get_report",
            description="Retrieve a specific report generated by an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "string",
                        "description": "The unique identifier of the report"
                    }
                },
                "required": ["report_id"]
            }
        ),
        Tool(
            name="list_reports",
            description="List reports with optional filters for task or agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "Filter by task ID"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Filter by agent ID"
                    }
                }
            }
        ),
        Tool(
            name="create_project",
            description="Create a new project that agents can work on",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description"
                    },
                    "repository_path": {
                        "type": "string",
                        "description": "Optional path to the project repository"
                    }
                },
                "required": ["name", "description"]
            }
        ),
        Tool(
            name="list_projects",
            description="List all available projects",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_project",
            description="Get detailed information about a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "The unique identifier of the project"
                    }
                },
                "required": ["project_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""

    try:
        if name == "list_agents":
            agent_type = arguments.get("agent_type")
            agents = await agent_manager.list_agents(agent_type)

            result = {
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "type": agent.type,
                        "description": agent.description,
                        "status": agent.status.value,
                        "capabilities": agent.capabilities,
                        "current_task": agent.current_task,
                        "last_activity": agent.last_activity.isoformat() if agent.last_activity else None
                    }
                    for agent in agents
                ],
                "total": len(agents)
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_agent_status":
            agent_id = arguments["agent_id"]
            agent = await agent_manager.get_agent(agent_id)

            if not agent:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Agent {agent_id} not found"})
                )]

            result = {
                "id": agent.id,
                "name": agent.name,
                "type": agent.type,
                "description": agent.description,
                "status": agent.status.value,
                "capabilities": agent.capabilities,
                "current_task": agent.current_task,
                "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
                "metadata": agent.metadata
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "assign_task":
            task = await agent_manager.create_task(
                agent_id=arguments["agent_id"],
                title=arguments["title"],
                description=arguments["description"],
                project_id=arguments.get("project_id"),
                context=arguments.get("context"),
                priority=arguments.get("priority", "medium")
            )

            result = {
                "task_id": task.id,
                "agent_id": task.agent_id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "message": "Task created successfully. Use execute_task to start execution."
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "execute_task":
            task_id = arguments["task_id"]
            task = await agent_manager.execute_task(task_id)

            result = {
                "task_id": task.id,
                "status": task.status.value,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "message": "Task execution started"
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_task_status":
            task_id = arguments["task_id"]
            task = await agent_manager.get_task(task_id)

            if not task:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Task {task_id} not found"})
                )]

            result = {
                "id": task.id,
                "agent_id": task.agent_id,
                "project_id": task.project_id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "result": task.result,
                "error": task.error
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "list_tasks":
            from .models import TaskStatus as TS

            tasks = await agent_manager.list_tasks(
                agent_id=arguments.get("agent_id"),
                status=TS(arguments["status"]) if arguments.get("status") else None,
                project_id=arguments.get("project_id")
            )

            result = {
                "tasks": [
                    {
                        "id": task.id,
                        "agent_id": task.agent_id,
                        "project_id": task.project_id,
                        "title": task.title,
                        "status": task.status.value,
                        "priority": task.priority.value,
                        "created_at": task.created_at.isoformat(),
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None
                    }
                    for task in tasks
                ],
                "total": len(tasks)
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_report":
            report_id = arguments["report_id"]
            report = await agent_manager.get_report(report_id)

            if not report:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Report {report_id} not found"})
                )]

            result = {
                "id": report.id,
                "task_id": report.task_id,
                "agent_id": report.agent_id,
                "title": report.title,
                "content": report.content,
                "format": report.format,
                "created_at": report.created_at.isoformat(),
                "metadata": report.metadata
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "list_reports":
            reports = await agent_manager.list_reports(
                task_id=arguments.get("task_id"),
                agent_id=arguments.get("agent_id")
            )

            result = {
                "reports": [
                    {
                        "id": report.id,
                        "task_id": report.task_id,
                        "agent_id": report.agent_id,
                        "title": report.title,
                        "format": report.format,
                        "created_at": report.created_at.isoformat()
                    }
                    for report in reports
                ],
                "total": len(reports)
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "create_project":
            project = await agent_manager.create_project(
                name=arguments["name"],
                description=arguments["description"],
                repository_path=arguments.get("repository_path")
            )

            result = {
                "project_id": project.id,
                "name": project.name,
                "description": project.description,
                "repository_path": project.repository_path,
                "created_at": project.created_at.isoformat(),
                "message": "Project created successfully"
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "list_projects":
            projects = await agent_manager.list_projects()

            result = {
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "repository_path": project.repository_path,
                        "agents": project.agents,
                        "created_at": project.created_at.isoformat()
                    }
                    for project in projects
                ],
                "total": len(projects)
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "get_project":
            project_id = arguments["project_id"]
            project = await agent_manager.get_project(project_id)

            if not project:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Project {project_id} not found"})
                )]

            result = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "repository_path": project.repository_path,
                "agents": project.agents,
                "created_at": project.created_at.isoformat(),
                "metadata": project.metadata
            }

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompts for common workflows"""
    return [
        Prompt(
            name="request_code_review",
            description="Request a code review from an appropriate agent",
            arguments=[
                {"name": "repository_path", "description": "Path to the code repository", "required": True},
                {"name": "focus_areas", "description": "Specific areas to focus on", "required": False}
            ]
        ),
        Prompt(
            name="request_performance_analysis",
            description="Request a performance analysis from an agent",
            arguments=[
                {"name": "repository_path", "description": "Path to the code repository", "required": True},
                {"name": "target_files", "description": "Specific files to analyze", "required": False}
            ]
        ),
        Prompt(
            name="request_debugging_help",
            description="Request debugging assistance from an agent",
            arguments=[
                {"name": "error_description", "description": "Description of the error", "required": True},
                {"name": "stack_trace", "description": "Stack trace if available", "required": False}
            ]
        )
    ]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific prompt"""

    if name == "request_code_review":
        repository_path = arguments.get("repository_path", "") if arguments else ""
        focus_areas = arguments.get("focus_areas", "general code quality") if arguments else "general code quality"

        return GetPromptResult(
            description="Code review request template",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Please perform a code review on the repository at: {repository_path}

Focus areas: {focus_areas}

Please analyze:
1. Code quality and best practices
2. Potential bugs or issues
3. Security vulnerabilities
4. Performance optimizations
5. Documentation completeness

Provide a detailed report with specific recommendations."""
                    )
                )
            ]
        )

    elif name == "request_performance_analysis":
        repository_path = arguments.get("repository_path", "") if arguments else ""
        target_files = arguments.get("target_files", "all files") if arguments else "all files"

        return GetPromptResult(
            description="Performance analysis request template",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""Please perform a performance analysis on: {repository_path}

Target files: {target_files}

Please analyze:
1. CPU-intensive operations
2. Memory usage patterns
3. I/O bottlenecks
4. Algorithm complexity
5. Caching opportunities

Provide specific optimization recommendations with estimated impact."""
                    )
                )
            ]
        )

    elif name == "request_debugging_help":
        error_description = arguments.get("error_description", "") if arguments else ""
        stack_trace = arguments.get("stack_trace", "Not provided") if arguments else "Not provided"

        return GetPromptResult(
            description="Debugging assistance request template",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"""I need help debugging the following issue:

Error Description:
{error_description}

Stack Trace:
{stack_trace}

Please:
1. Analyze the error and identify the root cause
2. Suggest potential fixes
3. Recommend preventive measures
4. Provide code examples if applicable"""
                    )
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server"""
    # Initialize agent manager
    await agent_manager.initialize()

    # Run the server
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
