"""Report API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
from pathlib import Path

# Add MCP server to path
mcp_server_path = Path(__file__).parent.parent.parent.parent / "mcp-server" / "src"
sys.path.insert(0, str(mcp_server_path))

from agent_mcp.agent_manager import agent_manager

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_reports(task_id: Optional[str] = None, agent_id: Optional[str] = None):
    """List all reports"""
    reports = await agent_manager.list_reports(task_id=task_id, agent_id=agent_id)

    return [
        {
            "id": report.id,
            "task_id": report.task_id,
            "agent_id": report.agent_id,
            "title": report.title,
            "format": report.format,
            "created_at": report.created_at.isoformat(),
            "metadata": report.metadata,
        }
        for report in reports
    ]


@router.get("/{report_id}", response_model=dict)
async def get_report(report_id: str):
    """Get a specific report"""
    report = await agent_manager.get_report(report_id)

    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    return {
        "id": report.id,
        "task_id": report.task_id,
        "agent_id": report.agent_id,
        "title": report.title,
        "content": report.content,
        "format": report.format,
        "created_at": report.created_at.isoformat(),
        "metadata": report.metadata,
    }
