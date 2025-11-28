"""Research Lab - Single-Intake Backend with Reports Archive"""
import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.database import init_db, get_db
from app.models import Session, SessionStatus, Report, Agent, AgentStatus
from app.agent_orchestrator import agent_orchestrator
from app.streaming import streaming_manager, StreamEventType
from app.logging import setup_logging, get_logger
from app.routes.auth import router as auth_router
from app.code_extractor import code_extractor
from app.agent_memory import agent_memory

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Research Lab API",
    version="2.1.0",
    description="Research platform with reports archive and agent learning"
)

# CORS
print(f"[CORS] Configuring with origins: {settings.CORS_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

# Initialize database
try:
    init_db()
    logger.info("Database initialized")
except Exception as e:
    logger.warning(f"Database init warning: {e}")


# ============================================================================
# SCHEMAS
# ============================================================================

class ResearchRequest(BaseModel):
    query: str
    agent_id: str = "research-agent"


# ============================================================================
# RESEARCH PROCESSING WITH LEARNING
# ============================================================================

async def process_research(session_id: str, query: str):
    """Process a research query, save report, and learn from it"""
    start_time = datetime.utcnow()

    try:
        # Let WebSocket connect
        await asyncio.sleep(0.5)

        # Send thinking status
        await streaming_manager.send_event(
            session_id,
            StreamEventType.AGENT_THINKING,
            {"message": "Analyzing your research question..."}
        )

        # Use the orchestrator if available
        if agent_orchestrator.enabled:
            await streaming_manager.send_event(
                session_id,
                StreamEventType.TOOL_CALL,
                {"tool": "research", "message": "Conducting research..."}
            )

            result = await agent_orchestrator.execute_task(
                task_id=session_id,
                task_title=query,
                task_description=query,
                agent_name="Research Agent",
                agent_type="research"
            )

            if result.get("status") == "completed":
                response_text = result.get("final_report", "Research completed.")
            else:
                response_text = f"Research encountered an issue: {result.get('error', 'Unknown error')}"
        else:
            # Fallback without AI
            await asyncio.sleep(1)
            response_text = f"""Research Query: "{query}"

The AI research engine requires an API key to be configured.

To enable full research capabilities, set the GEMINI_API_KEY environment variable.

Your query has been recorded in the session archive."""

        # Stream response
        await streaming_manager.stream_agent_response(session_id, response_text)

        # Complete session
        await streaming_manager.complete_session(
            session_id,
            final_output=response_text,
            artifacts=[]
        )

        # === SAVE AS REPORT ===
        elapsed = datetime.utcnow() - start_time

        with get_db() as db:
            # Create report in database
            report_id = str(uuid.uuid4())
            report = Report(
                id=report_id,
                task_id=session_id,
                agent_id="research-agent",
                project_id="default",
                title=f"Research: {query[:100]}",
                content=response_text,
                summary=response_text[:500] if len(response_text) > 500 else response_text,
                format="markdown",
                tags=["research", "ai-generated", agent_orchestrator.llm_provider if agent_orchestrator.enabled else "fallback"],
                meta={
                    "session_id": session_id,
                    "duration_seconds": elapsed.total_seconds(),
                    "query": query,
                    "ai_provider": agent_orchestrator.llm_provider if agent_orchestrator.enabled else "none"
                }
            )
            db.add(report)
            db.commit()

            logger.info(f"Report saved: {report_id}")

            # === AGENT LEARNING ===
            if agent_orchestrator.enabled and len(response_text) > 500:
                try:
                    # Extract code and learn skills
                    learning_result = code_extractor.learn_from_report(
                        agent_name="Research Agent",
                        report_content=response_text,
                        task_title=query
                    )

                    if learning_result.get("skills_learned", 0) > 0:
                        logger.info(f"Agent learned {learning_result['skills_learned']} new skills")

                    # Record in agent memory
                    agent_memory.record_task_completion(
                        agent_id="research-agent",
                        task_id=session_id,
                        task_title=query,
                        duration_seconds=elapsed.total_seconds(),
                        sources_found=0,
                        skills_utilized=["research", "analysis"],
                        report_id=report_id
                    )
                except Exception as e:
                    logger.warning(f"Agent learning error (non-fatal): {e}")

    except Exception as e:
        logger.error(f"Research error for session {session_id}: {e}")
        await streaming_manager.send_event(
            session_id,
            StreamEventType.ERROR,
            {"message": f"Error: {str(e)}"}
        )

        with get_db() as db:
            session = db.query(Session).filter(Session.id == session_id).first()
            if session:
                session.status = SessionStatus.FAILED
                db.commit()


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.1.0",
        "ai_enabled": agent_orchestrator.enabled,
        "ai_provider": getattr(agent_orchestrator, 'llm_provider', 'none')
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Research Lab API",
        "version": "2.1.0",
        "docs": "/docs"
    }


# ============================================================================
# SESSIONS
# ============================================================================

@app.post("/api/sessions")
async def create_session(request: ResearchRequest):
    """Create a new research session"""
    session_id = str(uuid.uuid4())

    with get_db() as db:
        session = Session(
            id=session_id,
            agent_id=request.agent_id,
            initial_query=request.query,
            status=SessionStatus.IN_PROGRESS
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Start background processing
        asyncio.create_task(process_research(session_id, request.query))

        return {
            "id": session.id,
            "agent_id": session.agent_id,
            "initial_query": session.initial_query,
            "status": session.status.value,
            "start_time": session.start_time.isoformat() if session.start_time else None
        }


@app.get("/api/sessions")
async def list_sessions(limit: int = 50):
    """List recent research sessions"""
    with get_db() as db:
        sessions = db.query(Session).order_by(Session.start_time.desc()).limit(limit).all()

        return [
            {
                "id": s.id,
                "initial_query": s.initial_query,
                "status": s.status.value,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_seconds": s.duration_seconds
            }
            for s in sessions
        ]


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    from app.models import InteractionLog, Artifact

    with get_db() as db:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        logs = db.query(InteractionLog).filter(
            InteractionLog.session_id == session_id
        ).order_by(InteractionLog.timestamp).all()

        artifacts = db.query(Artifact).filter(
            Artifact.session_id == session_id
        ).all()

        return {
            "id": session.id,
            "initial_query": session.initial_query,
            "final_output": session.final_output,
            "status": session.status.value,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_seconds": session.duration_seconds,
            "interaction_logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "event_type": log.event_type.value,
                    "content": log.content
                }
                for log in logs
            ],
            "artifacts": [
                {
                    "id": a.id,
                    "type": a.artifact_type.value,
                    "title": a.title
                }
                for a in artifacts
            ]
        }


# ============================================================================
# REPORTS (Library)
# ============================================================================

@app.get("/api/reports")
async def list_reports(limit: int = 50):
    """List all research reports"""
    with get_db() as db:
        reports = db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary[:200] if r.summary else None,
                "tags": r.tags or [],
                "format": r.format,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "meta": r.meta or {}
            }
            for r in reports
        ]


@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get full report content"""
    with get_db() as db:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return {
            "id": report.id,
            "title": report.title,
            "content": report.content,
            "summary": report.summary,
            "tags": report.tags or [],
            "format": report.format,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "meta": report.meta or {}
        }


@app.get("/api/reports/search")
async def search_reports(q: str, limit: int = 20):
    """Search reports by title or content"""
    with get_db() as db:
        reports = db.query(Report).filter(
            (Report.title.ilike(f"%{q}%")) | (Report.content.ilike(f"%{q}%"))
        ).order_by(Report.created_at.desc()).limit(limit).all()

        return [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary[:200] if r.summary else None,
                "tags": r.tags or [],
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reports
        ]


# ============================================================================
# AGENTS
# ============================================================================

@app.get("/api/agents")
async def list_agents():
    """List all agents"""
    with get_db() as db:
        agents = db.query(Agent).all()

        return [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "specialization": a.specialization,
                "status": a.status.value if a.status else "idle",
                "capabilities": a.capabilities or [],
                "last_active": a.last_active.isoformat() if a.last_active else None
            }
            for a in agents
        ]


@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    with get_db() as db:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "specialization": agent.specialization,
            "status": agent.status.value if agent.status else "idle",
            "capabilities": agent.capabilities or [],
            "config": agent.config or {},
            "last_active": agent.last_active.isoformat() if agent.last_active else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None
        }


# ============================================================================
# CAPABILITIES / STATS
# ============================================================================

@app.get("/api/capabilities")
async def get_capabilities():
    """Get platform capabilities"""
    with get_db() as db:
        agent_count = db.query(Agent).count()
        report_count = db.query(Report).count()
        session_count = db.query(Session).count()

    return {
        "total_agents": agent_count if agent_count > 0 else 1,
        "total_reports": report_count,
        "total_sessions": session_count,
        "by_type": {
            "research": [{
                "name": "Research Agent",
                "specialization": "Comprehensive research and analysis",
                "capabilities": ["web_search", "analysis", "report_generation"],
                "status": "idle"
            }]
        },
        "available_tools": ["research", "analysis", "report_generation"],
        "ai_enabled": agent_orchestrator.enabled,
        "ai_provider": getattr(agent_orchestrator, 'llm_provider', 'none'),
        "features": {
            "reports_library": True,
            "agent_learning": True,
            "streaming": True
        }
    }


@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    with get_db() as db:
        return {
            "agents": db.query(Agent).count(),
            "reports": db.query(Report).count(),
            "sessions": {
                "total": db.query(Session).count(),
                "completed": db.query(Session).filter(Session.status == SessionStatus.COMPLETED).count(),
                "in_progress": db.query(Session).filter(Session.status == SessionStatus.IN_PROGRESS).count()
            }
        }


# ============================================================================
# WEBSOCKET
# ============================================================================

@app.websocket("/ws/stream/{session_id}")
async def streaming_websocket(websocket: WebSocket, session_id: str):
    """WebSocket for streaming research results"""
    await streaming_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
