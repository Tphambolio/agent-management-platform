"""
RAG (Retrieval-Augmented Generation) API Routes

Provides endpoints for:
- Automatic knowledge ingestion from research reports
- Agent memory queries (semantic search)
- Memory management
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import HTTPException

from .vector_store import get_vector_store
from .models import Report, Agent
from .database import get_db

logger = logging.getLogger(__name__)


# === Pydantic Models === #

class MemoryIngestRequest(BaseModel):
    """Request to manually ingest a report into vector memory"""
    report_id: str = Field(..., description="ID of the report to ingest")
    is_shared_knowledge: bool = Field(
        default=False,
        description="Whether to store in shared organizational knowledge"
    )


class MemoryQueryRequest(BaseModel):
    """Request to query agent memory"""
    query: str = Field(..., description="Natural language query", min_length=1)
    k: int = Field(default=4, description="Number of results to retrieve", ge=1, le=20)
    access_shared_knowledge: bool = Field(
        default=True,
        description="Whether to include shared organizational knowledge"
    )


class MemoryQueryResponse(BaseModel):
    """Response from memory query"""
    status: str
    query: str
    agent_id: str
    retrieved_documents: List[Dict[str, Any]]
    context: str
    total_results: int
    unique_results: int


class MemoryIngestResponse(BaseModel):
    """Response from memory ingestion"""
    status: str
    report_id: str
    collection: str
    chunks_ingested: int


# === Helper Functions === #

async def auto_ingest_report_to_memory(
    report_id: str,
    agent_id: str,
    report_title: str,
    report_content: str,
    is_shared: bool = False
) -> Dict[str, Any]:
    """
    Automatically ingest a report into the vector store.
    Called after report creation.

    Args:
        report_id: UUID of the report
        agent_id: UUID of the agent that created the report
        report_title: Title of the report
        report_content: Full markdown content
        is_shared: Whether to store in shared knowledge

    Returns:
        Dict with ingestion status
    """
    try:
        vector_store = get_vector_store()
        result = await vector_store.ingest_report(
            agent_id=agent_id,
            report_id=report_id,
            report_title=report_title,
            report_content=report_content,
            is_shared_knowledge=is_shared,
            metadata={"auto_ingested": True}
        )
        logger.info(f"✅ Auto-ingested report {report_id} to vector memory")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to auto-ingest report {report_id}: {str(e)}", exc_info=True)
        return {"status": "error", "error": str(e)}


# === RAG Routes === #

def register_rag_routes(app):
    """Register RAG routes with the FastAPI app"""

    @app.post("/api/agents/{agent_id}/query-memory", response_model=MemoryQueryResponse)
    async def query_agent_memory(agent_id: str, request: MemoryQueryRequest):
        """
        Query an agent's private memory and shared organizational knowledge.

        Performs semantic search across the agent's accumulated knowledge from
        past research reports. Returns relevant context for augmenting LLM responses.

        **Use Case:** Agent needs contextual information from past research to
        answer a new question or generate a new report.
        """
        logger.info(f"🔍 Agent '{agent_id}' querying memory: '{request.query[:100]}'")

        # Verify agent exists
        async with get_db() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # Query vector store
        vector_store = get_vector_store()
        result = await vector_store.query_agent_memory(
            agent_id=agent_id,
            query=request.query,
            k=request.k,
            access_shared_knowledge=request.access_shared_knowledge
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Query failed"))

        return MemoryQueryResponse(**result)

    @app.post("/api/reports/{report_id}/ingest", response_model=MemoryIngestResponse)
    async def ingest_report_to_memory(report_id: str, request: MemoryIngestRequest):
        """
        Manually ingest a research report into the vector store.

        This endpoint allows manual triggering of knowledge ingestion.
        Normally, reports are auto-ingested upon creation.

        **Use Case:** Re-ingest a report that was created before RAG was enabled,
        or ingest with different settings (e.g., mark as shared knowledge).
        """
        logger.info(f"📥 Manual ingestion requested for report '{report_id}'")

        # Fetch report from database
        async with get_db() as db:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")

            # Ingest to vector store
            vector_store = get_vector_store()
            result = await vector_store.ingest_report(
                agent_id=report.agent_id,
                report_id=report.id,
                report_title=report.title,
                report_content=report.content,
                is_shared_knowledge=request.is_shared_knowledge,
                metadata={
                    "manual_ingest": True,
                    "task_id": report.task_id,
                    "project_id": report.project_id
                }
            )

            if result["status"] == "error":
                raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed"))

            return MemoryIngestResponse(**result)

    @app.post("/api/knowledge/shared/query", response_model=MemoryQueryResponse)
    async def query_shared_knowledge(request: MemoryQueryRequest):
        """
        Query only the shared organizational knowledge base.

        Searches across all reports marked as shared knowledge,
        without filtering by agent.

        **Use Case:** Find organizational best practices, guidelines,
        or cross-agent research findings.
        """
        logger.info(f"🔍 Querying shared knowledge: '{request.query[:100]}'")

        vector_store = get_vector_store()

        # Query shared collection directly by using a non-existent agent_id
        # and forcing shared knowledge access
        result = await vector_store.query_agent_memory(
            agent_id="__shared_only__",  # Placeholder - won't match any private memory
            query=request.query,
            k=request.k,
            access_shared_knowledge=True  # Only shared knowledge will be returned
        )

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Query failed"))

        return MemoryQueryResponse(**result)

    @app.delete("/api/agents/{agent_id}/memory")
    async def delete_agent_memory(agent_id: str):
        """
        Delete all private memory for a specific agent.

        **Warning:** This action is irreversible. The agent's accumulated
        knowledge from past research will be permanently deleted.

        **Use Case:** Agent is being decommissioned or needs a fresh start.
        """
        logger.info(f"🗑️  Deleting memory for agent '{agent_id}'")

        # Verify agent exists
        async with get_db() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

        # Delete from vector store
        vector_store = get_vector_store()
        result = await vector_store.delete_agent_memory(agent_id=agent_id)

        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result.get("error", "Deletion failed"))

        return {
            "status": "success",
            "message": f"Deleted all private memory for agent '{agent_id}'",
            **result
        }

    @app.get("/api/agents/{agent_id}/memory/stats")
    async def get_agent_memory_stats(agent_id: str):
        """
        Get statistics about an agent's accumulated knowledge.

        Returns information about how many reports have been ingested,
        number of chunks stored, etc.

        **Use Case:** Monitor agent learning progress, debug memory issues.
        """
        logger.info(f"📊 Fetching memory stats for agent '{agent_id}'")

        # Verify agent exists
        async with get_db() as db:
            agent = db.query(Agent).filter(Agent.id == agent_id).first()
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

            # Count reports from this agent
            report_count = db.query(Report).filter(Report.agent_id == agent_id).count()

        # TODO: Add actual vector store stats (requires ChromaDB collection introspection)
        # For now, return basic stats

        return {
            "agent_id": agent_id,
            "agent_name": agent.name if agent else "Unknown",
            "total_reports_created": report_count,
            "status": "RAG memory system active",
            "note": "Detailed vector store stats coming in next update"
        }

    logger.info("✅ RAG routes registered successfully")
