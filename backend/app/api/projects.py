"""Project API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sys
from pathlib import Path

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from agent_mcp.agent_manager import agent_manager

router = APIRouter()


class CreateProjectRequest(BaseModel):
    name: str
    description: str
    repository_path: Optional[str] = None


@router.get("/", response_model=List[dict])
async def list_projects():
    """List all projects"""
    projects = await agent_manager.list_projects()

    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "repository_path": project.repository_path,
            "agents": project.agents,
            "created_at": project.created_at.isoformat(),
        }
        for project in projects
    ]


@router.post("/", response_model=dict)
async def create_project(request: CreateProjectRequest):
    """Create a new project"""
    project = await agent_manager.create_project(
        name=request.name,
        description=request.description,
        repository_path=request.repository_path
    )

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "repository_path": project.repository_path,
        "created_at": project.created_at.isoformat(),
        "message": "Project created successfully"
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str):
    """Get a specific project"""
    project = await agent_manager.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "repository_path": project.repository_path,
        "agents": project.agents,
        "created_at": project.created_at.isoformat(),
        "metadata": project.metadata,
    }


@router.get("/{project_id}/tasks", response_model=List[dict])
async def get_project_tasks(project_id: str):
    """Get all tasks for a project"""
    project = await agent_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    tasks = await agent_manager.list_tasks(project_id=project_id)

    return [
        {
            "id": task.id,
            "agent_id": task.agent_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        for task in tasks
    ]
