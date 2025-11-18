"""Database models for Agent Management Platform"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Enum as SQLEnum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class AgentStatus(str, enum.Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    OFFLINE = "offline"


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    meta = Column(JSON, default=dict)


class Agent(Base):
    """Agent model"""
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(100), nullable=False)  # domain, development, coordination
    specialization = Column(String(255), nullable=False)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.IDLE)
    capabilities = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    prompt_file = Column(String(500))  # Path to agent prompt
    last_active = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict


class Task(Base):
    """Task model"""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(Integer, default=1)
    context = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict


class Report(Base):
    """Report model"""
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    project_id = Column(String, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    format = Column(String(50), default="markdown")  # markdown, json, html
    summary = Column(Text)
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    meta = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, enum.Enum):
    """Interaction event type enumeration"""
    USER_INPUT = "user_input"
    AGENT_THOUGHT = "agent_thought"
    TOOL_CALL = "tool_call"
    TOOL_OUTPUT = "tool_output"
    LLM_RESPONSE = "llm_response"
    ERROR = "error"
    STATUS_UPDATE = "status_update"


class ArtifactType(str, enum.Enum):
    """Artifact type enumeration"""
    RESEARCH_SUMMARY = "research_summary"
    CODE_SNIPPET = "code_snippet"
    DOCUMENT = "document"
    DATA_ANALYSIS = "data_analysis"
    DIAGRAM = "diagram"
    REPORT = "report"


class Session(Base):
    """
    Session model for tracking user-agent interactions
    Based on research recommendations for comprehensive archiving
    """
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)  # Optional: for multi-user support
    agent_id = Column(String, nullable=False, index=True)
    initial_query = Column(Text, nullable=False)
    final_output = Column(Text)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.IN_PROGRESS, index=True)
    agent_model_id = Column(String(255))  # e.g., 'claude-sonnet-4', 'gpt-4'
    cost_estimate_usd = Column(Integer)  # Store as cents to avoid decimal issues
    duration_seconds = Column(Integer)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    meta = Column(JSON, default=dict)


class InteractionLog(Base):
    """
    Interaction log for tracking every step within a session
    Enables full audit trail and replay capability
    """
    __tablename__ = "interaction_logs"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    content = Column(JSON)  # Structured event data
    agent_state = Column(JSON)  # Optional: snapshot of agent internal state
    token_count = Column(Integer)
    cost_estimate_usd = Column(Integer)  # Store as cents
    meta = Column(JSON, default=dict)


class Artifact(Base):
    """
    Artifact model for storing research results, code, documents
    Part of the comprehensive archive system
    """
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    artifact_type = Column(SQLEnum(ArtifactType), nullable=False, index=True)
    title = Column(String(500))
    content = Column(Text)  # Main content
    file_path = Column(String(512))  # Optional: external file storage
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(JSON, default=list)
    meta = Column(JSON, default=dict)  # Language, sources, etc.


class Project(Base):
    """Project model"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    repository_path = Column(String(500))
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    meta = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict
