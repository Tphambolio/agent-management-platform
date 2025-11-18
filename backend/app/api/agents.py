"""Agent API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
from pathlib import Path

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from agent_mcp.agent_manager import agent_manager
from agent_mcp.models import Agent

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_agents(agent_type: Optional[str] = None):
    """List all agents"""
    agents = await agent_manager.list_agents(agent_type)

    return [
        {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "description": agent.description,
            "status": agent.status.value,
            "capabilities": agent.capabilities,
            "current_task": agent.current_task,
            "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
        }
        for agent in agents
    ]


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str):
    """Get a specific agent"""
    agent = await agent_manager.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    return {
        "id": agent.id,
        "name": agent.name,
        "type": agent.type,
        "description": agent.description,
        "status": agent.status.value,
        "capabilities": agent.capabilities,
        "current_task": agent.current_task,
        "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
        "metadata": agent.metadata,
    }


@router.get("/{agent_id}/tasks", response_model=List[dict])
async def get_agent_tasks(agent_id: str):
    """Get all tasks for a specific agent"""
    agent = await agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    tasks = await agent_manager.list_tasks(agent_id=agent_id)

    return [
        {
            "id": task.id,
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


@router.post("/rediscover")
async def rediscover_agents():
    """Rediscover agents from filesystem"""
    agents = await agent_manager.discover_agents()

    return {
        "message": "Agents rediscovered",
        "total": len(agents),
        "agents": [{"id": a.id, "name": a.name, "type": a.type} for a in agents]
    }
