"""Data models for Agent Management Platform"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status"""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Agent(BaseModel):
    """Agent model"""
    id: str
    name: str
    type: str  # domain, development, analysis, etc.
    description: str
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[str] = Field(default_factory=list)
    current_task: Optional[str] = None
    last_activity: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """Task model"""
    id: str
    agent_id: str
    project_id: Optional[str] = None
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class Report(BaseModel):
    """Report model"""
    id: str
    task_id: str
    agent_id: str
    title: str
    content: Dict[str, Any]
    format: str = "json"  # json, markdown, html
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    description: str
    repository_path: Optional[str] = None
    agents: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
