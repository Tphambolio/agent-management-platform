"""Pydantic schemas with comprehensive validation"""
from pydantic import BaseModel, validator, Field, constr
from typing import Optional, List, Dict, Any
from enum import Enum
import re
from datetime import datetime


# Enums
class AgentType(str, Enum):
    DOMAIN = "domain"
    DEVELOPMENT = "development"
    COORDINATION = "coordination"
    RESEARCH = "research"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


# Request Schemas
class CreateAgentRequest(BaseModel):
    name: constr(min_length=3, max_length=100)
    type: AgentType
    specialization: constr(min_length=3, max_length=200)
    capabilities: Optional[List[str]] = Field(default_factory=list, max_items=20)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        # Allow letters, numbers, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', v):
            raise ValueError('Name can only contain letters, numbers, spaces, hyphens, and underscores')
        return v.strip()

    @validator('capabilities', each_item=True)
    def validate_capability(cls, v):
        if len(v) > 500:
            raise ValueError('Each capability must be less than 500 characters')
        return v.strip()


class CreateTaskRequest(BaseModel):
    agent_id: constr(min_length=36, max_length=36)
    title: constr(min_length=3, max_length=200)
    description: constr(min_length=10, max_length=10000)
    project_id: Optional[constr(min_length=36, max_length=36)] = None
    priority: int = Field(default=2, ge=1, le=5)
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('agent_id', 'project_id')
    def validate_uuid(cls, v):
        if v and not re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            v,
            re.IGNORECASE
        ):
            raise ValueError('Must be a valid UUID')
        return v

    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace')
        if len(v.split()) < 3:
            raise ValueError('Description must contain at least 3 words')
        return v.strip()

    @validator('context')
    def validate_context(cls, v):
        # Ensure context is not too large
        import json
        if v and len(json.dumps(v)) > 50000:
            raise ValueError('Context data too large (max 50KB)')
        return v


class UpdateTaskRequest(BaseModel):
    title: Optional[constr(min_length=3, max_length=200)] = None
    description: Optional[constr(min_length=10, max_length=10000)] = None
    status: Optional[TaskStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

    @validator('title', 'description')
    def validate_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Cannot be empty or whitespace')
        return v.strip() if v else None


class CreateProjectRequest(BaseModel):
    name: constr(min_length=3, max_length=100)
    description: constr(min_length=10, max_length=1000)
    repository_path: Optional[constr(max_length=500)] = None

    @validator('name', 'description')
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Cannot be empty or whitespace')
        return v.strip()

    @validator('repository_path')
    def validate_repository_path(cls, v):
        if v:
            # Basic path validation
            if '..' in v or v.startswith('/etc') or v.startswith('/sys'):
                raise ValueError('Invalid repository path')
            return v.strip()
        return v


class ResearchRequest(BaseModel):
    topic: constr(min_length=3, max_length=500)
    agent_id: constr(min_length=36, max_length=36)
    requirements: Optional[str] = Field(None, max_length=5000)
    priority: int = Field(default=2, ge=1, le=5)

    @validator('agent_id')
    def validate_uuid(cls, v):
        if not re.match(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            v,
            re.IGNORECASE
        ):
            raise ValueError('Must be a valid UUID')
        return v

    @validator('topic')
    def validate_topic(cls, v):
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace')
        if len(v.split()) < 2:
            raise ValueError('Topic must contain at least 2 words')
        return v.strip()


# Response Schemas
class AgentResponse(BaseModel):
    id: str
    name: str
    type: str
    specialization: str
    status: str
    capabilities: List[str] = []
    created_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: str
    agent_id: str
    project_id: Optional[str] = None
    title: str
    description: str
    status: str
    priority: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: str
    task_id: str
    agent_id: str
    project_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    content: str
    format: str = "markdown"
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    agents_discovered: int
    tasks_total: int
    tasks_running: int
    reports_total: int
    database_connected: bool


class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    path: str


# Authentication Schemas
class RegisterRequest(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: constr(min_length=5, max_length=255)
    password: constr(min_length=8, max_length=100)
    full_name: Optional[constr(max_length=255)] = None

    @validator('username')
    def validate_username(cls, v):
        if not v.strip():
            raise ValueError('Username cannot be empty or whitespace')
        # Allow only alphanumeric and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        if not v.strip():
            raise ValueError('Email cannot be empty or whitespace')
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.strip().lower()

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        # Require at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
