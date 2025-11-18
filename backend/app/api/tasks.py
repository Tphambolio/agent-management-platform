"""Task API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sys
from pathlib import Path

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from agent_mcp.agent_manager import agent_manager
from agent_mcp.models import TaskStatus, TaskPriority

router = APIRouter()


class CreateTaskRequest(BaseModel):
    agent_id: str
    title: str
    description: str
    project_id: Optional[str] = None
    priority: str = "medium"
    context: Optional[Dict[str, Any]] = None


@router.get("/", response_model=List[dict])
async def list_tasks(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[str] = None
):
    """List all tasks with optional filters"""
    task_status = TaskStatus(status) if status else None
    tasks = await agent_manager.list_tasks(agent_id=agent_id, status=task_status, project_id=project_id)

    return [
        {
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
        }
        for task in tasks
    ]


@router.post("/", response_model=dict)
async def create_task(request: CreateTaskRequest):
    """Create a new task"""
    try:
        task = await agent_manager.create_task(
            agent_id=request.agent_id,
            title=request.title,
            description=request.description,
            project_id=request.project_id,
            context=request.context,
            priority=request.priority
        )

        return {
            "id": task.id,
            "agent_id": task.agent_id,
            "title": task.title,
            "status": task.status.value,
            "priority": task.priority.value,
            "created_at": task.created_at.isoformat(),
            "message": "Task created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str):
    """Get a specific task"""
    task = await agent_manager.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {
        "id": task.id,
        "agent_id": task.agent_id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "context": task.context,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "result": task.result,
        "error": task.error,
    }


@router.post("/{task_id}/execute")
async def execute_task(task_id: str):
    """Execute a task"""
    try:
        task = await agent_manager.execute_task(task_id)

        return {
            "id": task.id,
            "status": task.status.value,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "message": "Task execution started"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
