"""Agent Management Platform - FastAPI Backend"""
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

class SessionCreate(BaseModel):
    agent_id: str
    query: str

from app.config import settings
from app.database import init_db, get_db
from app.models import Agent, Task, Report, Project, AgentStatus, TaskStatus
from app.web_researcher import web_researcher
from app.local_agent_skills import local_agent_skills_system  # Use local CLI-based system
from app.agent_memory import agent_memory
from app.dataset_manager import dataset_manager
from app.code_extractor import code_extractor
# Import MCP + LangGraph orchestrator
from app.agent_orchestrator import agent_orchestrator
# Import streaming manager
from app.streaming import streaming_manager, StreamEventType
# Import error handlers
from app.middleware.error_handler import (
    AppException,
    NotFoundException,
    DatabaseException,
    handle_app_exception,
    handle_validation_error,
    handle_database_error,
    handle_generic_exception
)
# Import auth routes
from app.routes.auth import router as auth_router
# Import logging
from app.logging import setup_logging, get_logger
# Import request ID middleware
from app.middleware.request_id import RequestIDMiddleware
# Temporarily disabled to debug deployment
# from app.agent_executor import AgentExecutor

# Setup structured logging
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Cloud-based agent workforce management platform"
)

# Register exception handlers
app.add_exception_handler(AppException, handle_app_exception)
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(SQLAlchemyError, handle_database_error)
app.add_exception_handler(Exception, handle_generic_exception)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request ID middleware for tracking
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(auth_router)

# Initialize database and agent executor (initialize on first import, not on startup)
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.warning("Database initialization warning", error=str(e))

# Temporarily disabled to debug deployment
# try:
#     agent_executor = AgentExecutor(settings.AGENTS_DIR)
#     logger.info("Agent executor initialized", agents_dir=settings.AGENTS_DIR)
# except Exception as e:
#     logger.warning("Agent executor initialization warning", error=str(e))
agent_executor = None  # Disabled for debugging

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Background task processor
async def task_processor():
    """Process tasks: conduct real research and generate reports"""

    # Check if MCP orchestrator is enabled
    use_mcp_orchestrator = os.getenv("USE_MCP_ORCHESTRATOR", "true").lower() == "true"

    while True:
        try:
            await asyncio.sleep(5)  # Check every 5 seconds

            with get_db() as db:
                # Find running tasks that have been running for more than 30 seconds
                running_tasks = db.query(Task).filter(Task.status == TaskStatus.RUNNING).all()

                for task in running_tasks:
                    if task.started_at:
                        elapsed = datetime.utcnow() - task.started_at
                        if elapsed > timedelta(seconds=30):
                            # Get agent details
                            agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
                            agent_name = agent.name if agent else "Research Agent"
                            agent_type = agent.type if agent else "general"

                            # Try using MCP + LangGraph orchestrator first
                            if use_mcp_orchestrator and agent_orchestrator.enabled:
                                print(f"\n🚀 [MCP Orchestrator] Processing task: {task.title}")

                                orchestrator_result = await agent_orchestrator.execute_task(
                                    task_id=task.id,
                                    task_title=task.title,
                                    task_description=task.description,
                                    agent_name=agent_name,
                                    agent_type=agent_type
                                )

                                if orchestrator_result.get("status") == "completed":
                                    final_content = orchestrator_result.get("final_report", "")
                                    sources_found = orchestrator_result.get("research_sources", 0)
                                    skills_utilized = 0  # MCP orchestrator handles this differently

                                    print(f"✅ [MCP Orchestrator] Task completed | {sources_found} sources analyzed")
                                else:
                                    # Fallback to legacy system
                                    print(f"⚠️  [MCP Orchestrator] Failed, falling back to legacy system")
                                    use_mcp_orchestrator = False  # Disable for this iteration
                                    continue  # Re-process with legacy system

                            # Legacy system (fallback)
                            if not use_mcp_orchestrator or not agent_orchestrator.enabled:
                                # Step 1: Conduct real web research
                                print(f"\n🔬 [Legacy] Conducting research for task: {task.title}")
                                research_result = await web_researcher.conduct_research(
                                    task_title=task.title,
                                    task_description=task.description,
                                    agent_type=agent_name
                                )

                                # Step 2: Use agent's specialized skills to synthesize findings
                                print(f"🧠 [Legacy] Loading agent skills for {agent_name}")
                                skills_result = await local_agent_skills_system.execute_task_with_skills(
                                    agent_name=agent_name,
                                    task_title=task.title,
                                    task_description=task.description,
                                    research_data=research_result
                                )

                                # Combine web research with skills-based synthesis
                                if skills_result.get("status") == "success":
                                    final_content = skills_result["content"]
                                    skills_utilized = skills_result.get("skills_utilized", 0)
                                    sources_found = research_result.get("sources_found", 0)
                                    print(f"✅ Agent skills applied ({skills_utilized} knowledge items)")
                                else:
                                    # Fallback to basic research if skills synthesis fails
                                    final_content = research_result.get("content", "No content generated")
                                    skills_utilized = 0
                                    sources_found = research_result.get("sources_found", 0)
                                    print(f"⚠️  Skills synthesis unavailable, using basic research")

                            # Mark task as completed
                            task.status = TaskStatus.COMPLETED
                            task.completed_at = datetime.utcnow()

                            # Build task result based on which system was used
                            orchestration_method = "mcp_orchestrator" if (use_mcp_orchestrator and agent_orchestrator.enabled) else "legacy"

                            task.result = {
                                "message": f"Task completed using {orchestration_method}",
                                "duration": str(elapsed),
                                "sources_found": sources_found,
                                "search_queries": [],
                                "skills_utilized": skills_utilized > 0,
                                "orchestration": orchestration_method
                            }

                            # Create comprehensive report
                            report_tags = ["web-research", "task-completion", f"agent-{agent_type}"]
                            if orchestration_method == "mcp_orchestrator":
                                report_tags.extend(["mcp", "langgraph", "advanced-orchestration"])
                            else:
                                report_tags.append("legacy-system")

                            report = Report(
                                id=str(uuid.uuid4()),
                                task_id=task.id,
                                agent_id=task.agent_id,
                                project_id=task.project_id,
                                title=f"Research Report: {task.title}",
                                summary=f"Agent '{agent_name}' conducted research on '{task.title}'. Found {sources_found} relevant sources using {orchestration_method}.",
                                content=final_content,
                                format="markdown",
                                tags=report_tags,
                                meta={
                                    "duration_seconds": elapsed.total_seconds(),
                                    "agent_type": agent_type,
                                    "sources_count": sources_found,
                                    "orchestration_method": orchestration_method,
                                    "skills_utilized": skills_utilized > 0,
                                    "skills_knowledge_items": skills_utilized
                                }
                            )

                            db.add(report)
                            db.commit()

                            # Record task in agent's memory for learning
                            agent_memory.record_task_completion(
                                agent_id=task.agent_id,
                                task_id=task.id,
                                task_title=task.title,
                                duration_seconds=elapsed.total_seconds(),
                                sources_found=research_result.get("sources_found", 0),
                                skills_utilized=report.tags,
                                report_id=report.id
                            )

                            # Extract code from report and learn new skills
                            print(f"🧠 Extracting code and learning skills...")
                            learning_result = code_extractor.learn_from_report(
                                agent_name=agent_name,
                                report_content=final_content,
                                task_title=task.title
                            )

                            if learning_result.get("skills_learned", 0) > 0:
                                print(f"   ✅ Agent learned {learning_result['skills_learned']} new skills!")

                            # Broadcast completion with report info
                            await manager.broadcast({
                                "type": "task_completed",
                                "task_id": task.id,
                                "report_id": report.id,
                                "duration": str(elapsed),
                                "sources_found": sources_found,
                                "orchestration": orchestration_method
                            })

                            print(f"✅ Task {task.id} completed | Report {report.id} | {sources_found} sources | Method: {orchestration_method}")

        except Exception as e:
            print(f"⚠️  Task processor error: {e}")

@app.on_event("startup")
async def startup_event():
    """Start background task processor"""
    asyncio.create_task(task_processor())
    logger.info("Background task processor started")

# Pydantic schemas
class AgentResponse(BaseModel):
    id: str
    name: str
    type: str
    specialization: str
    status: str
    capabilities: List[str]
    prompt_file: Optional[str]
    last_active: Optional[str]

class TaskCreate(BaseModel):
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    project_id: Optional[str] = None
    title: str
    description: str
    priority: int = 1
    context: dict = {}

class TaskResponse(BaseModel):
    id: str
    agent_id: str
    project_id: str
    title: str
    description: str
    status: str
    priority: int
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    repository_path: Optional[str] = None

class AgentCreate(BaseModel):
    name: str
    type: str
    specialization: str
    capabilities: List[str] = []
    config: dict = {}
    prompt_file: Optional[str] = None

# ============================================================================
# AGENT ENDPOINTS
# ============================================================================

@app.get("/api/agents", response_model=List[AgentResponse])
async def list_agents(status: Optional[str] = None, type: Optional[str] = None):
    """List all agents"""
    with get_db() as db:
        query = db.query(Agent)
        if status:
            query = query.filter(Agent.status == status)
        if type:
            query = query.filter(Agent.type == type)
        agents = query.all()
        
        return [
            AgentResponse(
                id=agent.id,
                name=agent.name,
                type=agent.type,
                specialization=agent.specialization,
                status=agent.status.value,
                capabilities=agent.capabilities or [],
                prompt_file=agent.prompt_file,
                last_active=agent.last_active.isoformat() if agent.last_active else None
            )
            for agent in agents
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
            "status": agent.status.value,
            "capabilities": agent.capabilities or [],
            "config": agent.config or {},
            "prompt_file": agent.prompt_file,
            "last_active": agent.last_active.isoformat() if agent.last_active else None,
            "created_at": agent.created_at.isoformat() if agent.created_at else None
        }

@app.post("/api/agents")
async def create_agent(agent_data: AgentCreate):
    """Manually register a new agent"""
    with get_db() as db:
        # Check if agent already exists
        existing = db.query(Agent).filter(Agent.name == agent_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Agent with name '{agent_data.name}' already exists")

        # Create new agent
        agent_id = str(uuid.uuid4())
        agent = Agent(
            id=agent_id,
            name=agent_data.name,
            type=agent_data.type,
            specialization=agent_data.specialization,
            capabilities=agent_data.capabilities,
            config=agent_data.config,
            prompt_file=agent_data.prompt_file,
            status=AgentStatus.IDLE
        )

        db.add(agent)
        db.commit()

        # Broadcast agent creation
        await manager.broadcast({
            "type": "agent_created",
            "agent_id": agent_id,
            "name": agent.name
        })

        return {
            "id": agent_id,
            "name": agent.name,
            "type": agent.type,
            "specialization": agent.specialization,
            "message": "Agent registered successfully"
        }

@app.post("/api/agents/sync")
async def sync_agents():
    """Sync agents from filesystem"""
    if agent_executor is None:
        raise HTTPException(status_code=503, detail="Agent executor not available")
    agent_executor.sync_agents_to_db()
    await manager.broadcast({"type": "agents_synced"})
    return {"message": "Agents synced successfully"}

# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@app.get("/api/tasks", response_model=List[TaskResponse])
async def list_tasks(
    agent_id: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """List tasks"""
    with get_db() as db:
        query = db.query(Task)
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
        if project_id:
            query = query.filter(Task.project_id == project_id)
        if status:
            query = query.filter(Task.status == status)
        
        tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
        
        return [
            TaskResponse(
                id=task.id,
                agent_id=task.agent_id,
                project_id=task.project_id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                priority=task.priority,
                created_at=task.created_at.isoformat() if task.created_at else None,
                started_at=task.started_at.isoformat() if task.started_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None
            )
            for task in tasks
        ]

@app.post("/api/tasks")
async def create_task(task_data: TaskCreate):
    """Create and assign a task"""
    with get_db() as db:
        # Find agent
        if task_data.agent_id:
            agent = db.query(Agent).filter(Agent.id == task_data.agent_id).first()
        elif task_data.agent_name:
            agent = db.query(Agent).filter(Agent.name == task_data.agent_name).first()
        else:
            # Auto-select first available agent
            agent = db.query(Agent).filter(Agent.status == AgentStatus.IDLE).first()

        if not agent:
            raise HTTPException(status_code=404, detail="No suitable agent found")

        # Get or create default project if not specified
        project_id = task_data.project_id
        if not project_id:
            default_project = db.query(Project).filter(Project.name == "Default").first()
            if not default_project:
                default_project = Project(
                    id=str(uuid.uuid4()),
                    name="Default",
                    description="Default project for general tasks"
                )
                db.add(default_project)
                db.commit()
            project_id = default_project.id

        # Create task
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            agent_id=agent.id,
            project_id=project_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            context=task_data.context,
            status=TaskStatus.PENDING
        )
        
        db.add(task)
        db.commit()
        
        # Broadcast task creation
        await manager.broadcast({
            "type": "task_created",
            "task_id": task_id,
            "agent_id": agent.id
        })
        
        return {
            "id": task_id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "status": "created",
            "message": "Task created successfully"
        }

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task details"""
    with get_db() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {
            "id": task.id,
            "agent_id": task.agent_id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority,
            "context": task.context,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }

@app.post("/api/tasks/{task_id}/execute")
async def execute_task(task_id: str):
    """Execute a task"""
    with get_db() as db:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.status != TaskStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Task is not pending (status: {task.status.value})")

        # Update task status to running
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        db.commit()

        # Broadcast task execution
        await manager.broadcast({
            "type": "task_started",
            "task_id": task_id,
            "agent_id": task.agent_id
        })

        return {
            "id": task_id,
            "status": "running",
            "message": "Task execution started"
        }

# ============================================================================
# REPORT ENDPOINTS
# ============================================================================

@app.get("/api/reports")
async def list_reports(
    agent_id: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50
):
    """List reports"""
    with get_db() as db:
        query = db.query(Report)
        if agent_id:
            query = query.filter(Report.agent_id == agent_id)
        if project_id:
            query = query.filter(Report.project_id == project_id)
        
        reports = query.order_by(Report.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": report.id,
                "task_id": report.task_id,
                "agent_id": report.agent_id,
                "project_id": report.project_id,
                "title": report.title,
                "summary": report.summary,
                "format": report.format,
                "tags": report.tags or [],
                "created_at": report.created_at.isoformat() if report.created_at else None
            }
            for report in reports
        ]

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get report details"""
    with get_db() as db:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "id": report.id,
            "task_id": report.task_id,
            "agent_id": report.agent_id,
            "project_id": report.project_id,
            "title": report.title,
            "content": report.content,
            "summary": report.summary,
            "format": report.format,
            "tags": report.tags or [],
            "created_at": report.created_at.isoformat() if report.created_at else None
        }

# ============================================================================
# PROJECT ENDPOINTS
# ============================================================================

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    with get_db() as db:
        projects = db.query(Project).all()
        return [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "repository_path": project.repository_path,
                "created_at": project.created_at.isoformat() if project.created_at else None
            }
            for project in projects
        ]

@app.post("/api/projects")
async def create_project(project_data: ProjectCreate):
    """Create a new project"""
    with get_db() as db:
        # Check if project exists
        existing = db.query(Project).filter(Project.name == project_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Project already exists")
        
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name=project_data.name,
            description=project_data.description or "",
            repository_path=project_data.repository_path
        )
        
        db.add(project)
        db.commit()
        
        return {
            "id": project_id,
            "name": project.name,
            "message": "Project created successfully"
        }

# ============================================================================
# STATS ENDPOINT
# ============================================================================

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    with get_db() as db:
        total_agents = db.query(Agent).count()
        idle_agents = db.query(Agent).filter(Agent.status == AgentStatus.IDLE).count()
        running_agents = db.query(Agent).filter(Agent.status == AgentStatus.RUNNING).count()
        
        total_tasks = db.query(Task).count()
        pending_tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).count()
        running_tasks = db.query(Task).filter(Task.status == TaskStatus.RUNNING).count()
        completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
        
        total_reports = db.query(Report).count()
        total_projects = db.query(Project).count()
        
        return {
            "agents": {
                "total": total_agents,
                "idle": idle_agents,
                "running": running_agents
            },
            "tasks": {
                "total": total_tasks,
                "pending": pending_tasks,
                "running": running_tasks,
                "completed": completed_tasks
            },
            "reports": total_reports,
            "projects": total_projects
        }

# ============================================================================
# SESSION & ARCHIVE ENDPOINTS (Counter-Style Interaction)
# ============================================================================

@app.get("/api/sessions")
async def list_sessions(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """List agent sessions with filtering"""
    from app.models import Session, SessionStatus

    with get_db() as db:
        query = db.query(Session)
        if agent_id:
            query = query.filter(Session.agent_id == agent_id)
        if status:
            query = query.filter(Session.status == status)

        sessions = query.order_by(Session.start_time.desc()).limit(limit).all()

        return [
            {
                "id": s.id,
                "agent_id": s.agent_id,
                "initial_query": s.initial_query,
                "status": s.status.value,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "end_time": s.end_time.isoformat() if s.end_time else None,
                "duration_seconds": s.duration_seconds
            }
            for s in sessions
        ]

@app.post("/api/sessions")
async def create_session(request: SessionCreate):
    """Create a new agent session"""
    import uuid
    from datetime import datetime
    from app.models import Session, SessionStatus

    agent_id = request.agent_id
    query = request.query

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    session_id = str(uuid.uuid4())

    with get_db() as db:
        session = Session(
            id=session_id,
            agent_id=agent_id,
            initial_query=query,
            status=SessionStatus.IN_PROGRESS,
            start_time=datetime.utcnow()
        )
        db.add(session)
        db.commit()

        return {
            "id": session.id,
            "agent_id": session.agent_id,
            "initial_query": session.initial_query,
            "status": session.status.value,
            "start_time": session.start_time.isoformat()
        }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details with full interaction log"""
    from app.models import Session, InteractionLog, Artifact

    with get_db() as db:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get interaction logs
        logs = db.query(InteractionLog).filter(
            InteractionLog.session_id == session_id
        ).order_by(InteractionLog.timestamp).all()

        # Get artifacts
        artifacts = db.query(Artifact).filter(
            Artifact.session_id == session_id
        ).all()

        return {
            "id": session.id,
            "agent_id": session.agent_id,
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
                    "title": a.title,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in artifacts
            ]
        }

@app.get("/api/artifacts")
async def list_artifacts(
    session_id: Optional[str] = None,
    artifact_type: Optional[str] = None,
    limit: int = 50
):
    """List artifacts with filtering"""
    from app.models import Artifact

    with get_db() as db:
        query = db.query(Artifact)
        if session_id:
            query = query.filter(Artifact.session_id == session_id)
        if artifact_type:
            query = query.filter(Artifact.artifact_type == artifact_type)

        artifacts = query.order_by(Artifact.timestamp.desc()).limit(limit).all()

        return [
            {
                "id": a.id,
                "session_id": a.session_id,
                "type": a.artifact_type.value,
                "title": a.title,
                "tags": a.tags,
                "timestamp": a.timestamp.isoformat()
            }
            for a in artifacts
        ]

@app.get("/api/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get full artifact content"""
    from app.models import Artifact

    with get_db() as db:
        artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")

        return {
            "id": artifact.id,
            "session_id": artifact.session_id,
            "type": artifact.artifact_type.value,
            "title": artifact.title,
            "content": artifact.content,
            "tags": artifact.tags,
            "meta": artifact.meta,
            "timestamp": artifact.timestamp.isoformat()
        }

@app.get("/api/archive/search")
async def search_archive(q: str, limit: int = 20):
    """Search across sessions and artifacts"""
    from app.models import Session, Artifact

    with get_db() as db:
        # Search sessions by query
        sessions = db.query(Session).filter(
            Session.initial_query.ilike(f"%{q}%")
        ).limit(limit).all()

        # Search artifacts by title/content
        artifacts = db.query(Artifact).filter(
            (Artifact.title.ilike(f"%{q}%")) | (Artifact.content.ilike(f"%{q}%"))
        ).limit(limit).all()

        return {
            "query": q,
            "sessions": [
                {
                    "id": s.id,
                    "initial_query": s.initial_query,
                    "status": s.status.value,
                    "start_time": s.start_time.isoformat() if s.start_time else None
                }
                for s in sessions
            ],
            "artifacts": [
                {
                    "id": a.id,
                    "title": a.title,
                    "type": a.artifact_type.value,
                    "timestamp": a.timestamp.isoformat()
                }
                for a in artifacts
            ]
        }

@app.get("/api/capabilities")
async def get_agent_capabilities():
    """Get list of all agent capabilities for discovery"""
    with get_db() as db:
        agents = db.query(Agent).all()

        # Organize by type
        capabilities_by_type = {}
        for agent in agents:
            agent_type = agent.type
            if agent_type not in capabilities_by_type:
                capabilities_by_type[agent_type] = []

            capabilities_by_type[agent_type].append({
                "name": agent.name,
                "specialization": agent.specialization,
                "capabilities": agent.capabilities or [],
                "status": agent.status.value
            })

        return {
            "total_agents": len(agents),
            "by_type": capabilities_by_type,
            "available_tools": [
                "web_search",
                "code_generation",
                "data_analysis",
                "geospatial_analysis",
                "document_generation"
            ]
        }

# ============================================================================
# WEBSOCKET (Enhanced with Streaming)
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/stream/{session_id}")
async def streaming_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket for streaming agent responses with enhanced intelligent orchestration
    Integrates: Gemini Planning + RAG Context + Agent Skills + Real Execution
    """
    from app.enhanced_orchestrator import enhanced_orchestrator

    await streaming_manager.connect(websocket, session_id)

    # Start enhanced orchestration (Gemini + RAG + Skills + Real Agents)
    asyncio.create_task(enhanced_orchestrator.process_session(session_id))

    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Client can send control messages (pause, cancel, etc.)
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        streaming_manager.disconnect(websocket, session_id)

# ============================================================================
# RESEARCH LAB - AI AGENTS
# ============================================================================

@app.post("/api/research")
async def request_research(
    topic: str,
    agent_name: str,
    depth: str = "comprehensive",
    output_format: str = "markdown"
):
    """Request AI agent to conduct research and generate report"""
    from app.research_lab import research_lab, ResearchRequest

    # Find agent
    with get_db() as db:
        agent = db.query(Agent).filter(Agent.name == agent_name).first()
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    # Create research request
    request = ResearchRequest(
        topic=topic,
        agent_type=agent.name,
        depth=depth,
        output_format=output_format
    )

    # Conduct research
    result = await research_lab.conduct_research(request)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Research failed"))

    # Save report to database
    report_id = str(uuid.uuid4())
    report = Report(
        id=report_id,
        agent_id=agent.id,
        project_id=None,  # Standalone research
        task_id=None,
        title=f"Research: {topic}",
        content=result["content"],
        summary=result["content"][:500],  # First 500 chars as summary
        format=output_format,
        tags=[agent.name, depth, "ai-generated"]
    )

    db.add(report)
    db.commit()

    return {
        "report_id": report_id,
        "agent": agent.name,
        "topic": topic,
        "word_count": result["word_count"],
        "generated_at": result["generated_at"],
        "content": result["content"]
    }

@app.get("/api/research/agents")
async def list_research_agents():
    """List available research agents"""
    research_capable_types = ["security", "analytics", "documentation", "architecture", "optimization", "quality"]

    with get_db() as db:
        agents = db.query(Agent).filter(Agent.type.in_(research_capable_types)).all()

        return [
            {
                "name": agent.name,
                "type": agent.type,
                "specialization": agent.specialization,
                "capabilities": agent.capabilities
            }
            for agent in agents
        ]

# ============================================================================
# KNOWLEDGE BASE ENDPOINTS
# ============================================================================

@app.get("/api/knowledge")
async def list_knowledge(limit: int = 20, agent_type: Optional[str] = None):
    """List knowledge base reports"""
    import sys
    sys.path.insert(0, '/home/rpas/wildfire-simulator-v2')
    from knowledge_base.storage import knowledge_base

    reports = knowledge_base.list_recent(limit=limit, agent_type=agent_type)
    return {"reports": reports, "count": len(reports)}

@app.get("/api/knowledge/search")
async def search_knowledge(q: str, limit: int = 10):
    """Search knowledge base"""
    import sys
    sys.path.insert(0, '/home/rpas/wildfire-simulator-v2')
    from knowledge_base.storage import knowledge_base

    results = knowledge_base.search(q, limit=limit)
    return {"results": results, "count": len(results), "query": q}

@app.get("/api/knowledge/stats")
async def knowledge_stats():
    """Get knowledge base statistics"""
    import sys
    sys.path.insert(0, '/home/rpas/wildfire-simulator-v2')
    from knowledge_base.storage import knowledge_base

    stats = knowledge_base.get_stats()
    return stats

@app.get("/api/knowledge/{report_id}")
async def get_knowledge_report(report_id: str):
    """Get full knowledge report"""
    import sys
    sys.path.insert(0, '/home/rpas/wildfire-simulator-v2')
    from knowledge_base.storage import knowledge_base

    report = knowledge_base.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report

@app.get("/api/knowledge/{report_id}/pdf")
async def serve_pdf(report_id: str):
    """Serve PDF file for a report"""
    import sys
    sys.path.insert(0, '/home/rpas/wildfire-simulator-v2')
    from knowledge_base.storage import knowledge_base
    from fastapi.responses import FileResponse

    report = knowledge_base.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_path = report.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.API_VERSION}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agent Management Platform API - AI Research Lab",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "features": ["agent_management", "task_assignment", "ai_research"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
