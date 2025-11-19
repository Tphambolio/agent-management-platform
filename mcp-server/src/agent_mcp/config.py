"""Configuration for Agent MCP Server"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """MCP Server settings"""

    # Paths
    AGENT_ROOT_DIR: Path = Path(__file__).parent.parent.parent.parent.parent / ".agents"
    DOMAIN_AGENTS_DIR: Path = AGENT_ROOT_DIR / "domain_agents"
    DEV_TEAM_DIR: Path = AGENT_ROOT_DIR / "development_team"
    REPORTS_DIR: Path = AGENT_ROOT_DIR / "development_team" / "reports"
    STATUS_DIR: Path = AGENT_ROOT_DIR / "development_team" / "status"
    TASKS_DIR: Path = AGENT_ROOT_DIR / "tasks"
    PROJECTS_DIR: Path = AGENT_ROOT_DIR / "projects"

    # Server settings
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENT_TASKS: int = 5
    TASK_TIMEOUT: int = 3600  # 1 hour in seconds

    # Agent execution
    PYTHON_PATH: str = "python3"
    AGENT_WRAPPER_SCRIPT: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables from backend


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.TASKS_DIR.mkdir(parents=True, exist_ok=True)
settings.PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
settings.STATUS_DIR.mkdir(parents=True, exist_ok=True)
