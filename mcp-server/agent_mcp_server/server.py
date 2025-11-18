"""MCP Server for Agent Management Platform"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Optional, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types
from pydantic import BaseModel, Field

from .database import init_db, get_db
from .models import Agent, Task, Report, Project, AgentStatus, TaskStatus
from .agent_executor import AgentExecutor


# Initialize MCP server
app = Server("agent-management-platform")

# Global agent executor
agent_executor: Optional[AgentExecutor] = None


class AgentInfo(BaseModel):
    """Agent information schema"""
    id: str
    name: str
    type: str
    specialization: str
    status: str
    capabilities: list[str] = Field(default_factory=list)


class TaskInfo(BaseModel):
    """Task information schema"""
    id: str
    agent_id: str
    project_id: str
    title: str
    description: str
    status: str
    priority: int = 1


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available MCP tools for agent management"""
    return [
        types.Tool(
            name="list_agents",
            description="List all registered agents and their current status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status (idle, running, error, offline)",
                        "enum": ["idle", "running", "error", "offline"]
                    },
                    "type": {
                        "type": "string",
                        "description": "Filter by type (domain, development, coordination)",
                        "enum": ["domain", "development", "coordination"]
                    }
                }
            }
        ),
        types.Tool(
            name="get_agent",
            description="Get detailed information about a specific agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "The unique ID of the agent"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "The name of the agent (alternative to agent_id)"
                    }
                },
                "oneOf": [
                    {"required": ["agent_id"]},
                    {"required": ["agent_name"]}
                ]
            }
        ),
        types.Tool(
            name="assign_task",
            description="Assign a new task to an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID of the agent to assign the task to"
                    },
                    "agent_name": {
                        "type": "string",
                        "description": "Name of the agent (alternative to agent_id)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "ID of the project this task belongs to"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed task description"
                    },
                    "priority": {
                        "type": "integer",
                        "description": "Task priority (1-5, higher is more urgent)",
                        "minimum": 1,
                        "maximum": 5,
                        "default": 1
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for the task (paths, configurations, etc.)"
                    },
                    "execute_now": {
                        "type": "boolean",
                        "description": "Execute the task immediately",
                        "default": True
                    }
                },
                "required": ["title", "description", "project_id"]
            }
        ),
        types.Tool(
            name="get_task_status",
            description="Get the current status of a task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The unique ID of the task"
                    }
                },
                "required": ["task_id"]
            }
        ),
        types.Tool(
            name="list_tasks",
            description="List tasks with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Filter by agent ID"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Filter by project ID"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status",
                        "enum": ["pending", "running", "completed", "failed", "cancelled"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return",
                        "default": 50,
                        "maximum": 500
                    }
                }
            }
        ),
        types.Tool(
            name="get_report",
            description="Retrieve a report generated by an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "report_id": {
                        "type": "string",
                        "description": "The unique ID of the report"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Get the report for a specific task (alternative)"
                    },
                    "format": {
                        "type": "string",
                        "description": "Desired format (markdown, json, html)",
                        "enum": ["markdown", "json", "html"],
                        "default": "markdown"
                    }
                },
                "oneOf": [
                    {"required": ["report_id"]},
                    {"required": ["task_id"]}
                ]
            }
        ),
        types.Tool(
            name="list_reports",
            description="List reports with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Filter by agent ID"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Filter by project ID"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of reports to return",
                        "default": 50,
                        "maximum": 500
                    }
                }
            }
        ),
        types.Tool(
            name="list_projects",
            description="List all projects",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="create_project",
            description="Create a new project",
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
                        "description": "Path to project repository"
                    },
                    "config": {
                        "type": "object",
                        "description": "Project configuration"
                    }
                },
                "required": ["name"]
            }
        ),
        types.Tool(
            name="register_agent",
            description="Register a new agent in the platform",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Agent name (must be unique)"
                    },
                    "type": {
                        "type": "string",
                        "description": "Agent type",
                        "enum": ["domain", "development", "coordination"]
                    },
                    "specialization": {
                        "type": "string",
                        "description": "Agent specialization (e.g., 'FBP Algorithm', 'Performance Tuning')"
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent capabilities"
                    },
                    "prompt_file": {
                        "type": "string",
                        "description": "Path to agent prompt file"
                    },
                    "config": {
                        "type": "object",
                        "description": "Agent configuration"
                    }
                },
                "required": ["name", "type", "specialization"]
            }
        ),
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests"""

    if arguments is None:
        arguments = {}

    try:
        if name == "list_agents":
            return await list_agents(arguments)
        elif name == "get_agent":
            return await get_agent(arguments)
        elif name == "assign_task":
            return await assign_task(arguments)
        elif name == "get_task_status":
            return await get_task_status(arguments)
        elif name == "list_tasks":
            return await list_tasks(arguments)
        elif name == "get_report":
            return await get_report(arguments)
        elif name == "list_reports":
            return await list_reports(arguments)
        elif name == "list_projects":
            return await list_projects(arguments)
        elif name == "create_project":
            return await create_project(arguments)
        elif name == "register_agent":
            return await register_agent(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


# Tool implementations

async def list_agents(args: dict) -> Sequence[types.TextContent]:
    """List all agents"""
    with get_db() as db:
        query = db.query(Agent)

        if "status" in args:
            query = query.filter(Agent.status == args["status"])
        if "type" in args:
            query = query.filter(Agent.type == args["type"])

        agents = query.all()

        result = {
            "total": len(agents),
            "agents": [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.type,
                    "specialization": agent.specialization,
                    "status": agent.status.value,
                    "capabilities": agent.capabilities,
                    "last_active": agent.last_active.isoformat() if agent.last_active else None
                }
                for agent in agents
            ]
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def get_agent(args: dict) -> Sequence[types.TextContent]:
    """Get agent details"""
    with get_db() as db:
        if "agent_id" in args:
            agent = db.query(Agent).filter(Agent.id == args["agent_id"]).first()
        elif "agent_name" in args:
            agent = db.query(Agent).filter(Agent.name == args["agent_name"]).first()
        else:
            raise ValueError("Either agent_id or agent_name must be provided")

        if not agent:
            raise ValueError("Agent not found")

        result = {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "specialization": agent.specialization,
            "status": agent.status.value,
            "capabilities": agent.capabilities,
            "config": agent.config,
            "prompt_file": agent.prompt_file,
            "last_active": agent.last_active.isoformat() if agent.last_active else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "meta": agent.meta
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def assign_task(args: dict) -> Sequence[types.TextContent]:
    """Assign a task to an agent"""
    with get_db() as db:
        # Find agent
        if "agent_id" in args:
            agent = db.query(Agent).filter(Agent.id == args["agent_id"]).first()
        elif "agent_name" in args:
            agent = db.query(Agent).filter(Agent.name == args["agent_name"]).first()
        else:
            # Auto-select best agent based on task description
            # For now, just get first available agent
            agent = db.query(Agent).filter(Agent.status == AgentStatus.IDLE).first()

        if not agent:
            raise ValueError("No suitable agent found")

        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            agent_id=agent.id,
            project_id=args.get("project_id", "default"),
            title=args["title"],
            description=args["description"],
            priority=args.get("priority", 1),
            context=args.get("context", {}),
            status=TaskStatus.PENDING
        )

        db.add(task)
        db.commit()

        # Execute task if requested
        if args.get("execute_now", True):
            # Update agent and task status
            agent.status = AgentStatus.RUNNING
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            db.commit()

            # Execute task asynchronously
            if agent_executor:
                asyncio.create_task(agent_executor.execute_task(task_id))

        result = {
            "task_id": task_id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "title": task.title,
            "status": task.status.value,
            "message": "Task created and queued for execution" if args.get("execute_now", True) else "Task created"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def get_task_status(args: dict) -> Sequence[types.TextContent]:
    """Get task status"""
    with get_db() as db:
        task = db.query(Task).filter(Task.id == args["task_id"]).first()

        if not task:
            raise ValueError("Task not found")

        result = {
            "id": task.id,
            "agent_id": task.agent_id,
            "project_id": task.project_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def list_tasks(args: dict) -> Sequence[types.TextContent]:
    """List tasks"""
    with get_db() as db:
        query = db.query(Task)

        if "agent_id" in args:
            query = query.filter(Task.agent_id == args["agent_id"])
        if "project_id" in args:
            query = query.filter(Task.project_id == args["project_id"])
        if "status" in args:
            query = query.filter(Task.status == args["status"])

        limit = args.get("limit", 50)
        tasks = query.order_by(Task.created_at.desc()).limit(limit).all()

        result = {
            "total": len(tasks),
            "tasks": [
                {
                    "id": task.id,
                    "agent_id": task.agent_id,
                    "project_id": task.project_id,
                    "title": task.title,
                    "status": task.status.value,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in tasks
            ]
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def get_report(args: dict) -> Sequence[types.TextContent]:
    """Get a report"""
    with get_db() as db:
        if "report_id" in args:
            report = db.query(Report).filter(Report.id == args["report_id"]).first()
        elif "task_id" in args:
            report = db.query(Report).filter(Report.task_id == args["task_id"]).first()
        else:
            raise ValueError("Either report_id or task_id must be provided")

        if not report:
            raise ValueError("Report not found")

        desired_format = args.get("format", "markdown")

        result = {
            "id": report.id,
            "task_id": report.task_id,
            "agent_id": report.agent_id,
            "project_id": report.project_id,
            "title": report.title,
            "summary": report.summary,
            "content": report.content,
            "format": report.format,
            "tags": report.tags,
            "created_at": report.created_at.isoformat() if report.created_at else None
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def list_reports(args: dict) -> Sequence[types.TextContent]:
    """List reports"""
    with get_db() as db:
        query = db.query(Report)

        if "agent_id" in args:
            query = query.filter(Report.agent_id == args["agent_id"])
        if "project_id" in args:
            query = query.filter(Report.project_id == args["project_id"])

        limit = args.get("limit", 50)
        reports = query.order_by(Report.created_at.desc()).limit(limit).all()

        result = {
            "total": len(reports),
            "reports": [
                {
                    "id": report.id,
                    "task_id": report.task_id,
                    "agent_id": report.agent_id,
                    "project_id": report.project_id,
                    "title": report.title,
                    "summary": report.summary,
                    "format": report.format,
                    "tags": report.tags,
                    "created_at": report.created_at.isoformat() if report.created_at else None
                }
                for report in reports
            ]
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def list_projects(args: dict) -> Sequence[types.TextContent]:
    """List projects"""
    with get_db() as db:
        projects = db.query(Project).all()

        result = {
            "total": len(projects),
            "projects": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "repository_path": project.repository_path,
                    "created_at": project.created_at.isoformat() if project.created_at else None
                }
                for project in projects
            ]
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def create_project(args: dict) -> Sequence[types.TextContent]:
    """Create a new project"""
    with get_db() as db:
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name=args["name"],
            description=args.get("description", ""),
            repository_path=args.get("repository_path"),
            config=args.get("config", {})
        )

        db.add(project)
        db.commit()

        result = {
            "id": project_id,
            "name": project.name,
            "message": "Project created successfully"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def register_agent(args: dict) -> Sequence[types.TextContent]:
    """Register a new agent"""
    with get_db() as db:
        # Check if agent with same name exists
        existing = db.query(Agent).filter(Agent.name == args["name"]).first()
        if existing:
            raise ValueError(f"Agent with name '{args['name']}' already exists")

        agent_id = str(uuid.uuid4())
        agent = Agent(
            id=agent_id,
            name=args["name"],
            type=args["type"],
            specialization=args["specialization"],
            capabilities=args.get("capabilities", []),
            prompt_file=args.get("prompt_file"),
            config=args.get("config", {}),
            status=AgentStatus.IDLE
        )

        db.add(agent)
        db.commit()

        result = {
            "id": agent_id,
            "name": agent.name,
            "type": agent.type,
            "specialization": agent.specialization,
            "message": "Agent registered successfully"
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


async def main():
    """Main entry point for the MCP server"""
    global agent_executor

    # Initialize database
    init_db()

    # Initialize agent executor
    from .agent_executor import AgentExecutor
    agent_executor = AgentExecutor()

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="agent-management-platform",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
