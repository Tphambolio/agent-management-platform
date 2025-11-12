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
