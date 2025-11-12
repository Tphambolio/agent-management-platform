"""Configuration for FastAPI backend"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    model_config = ConfigDict(extra='allow', env_file=".env", env_file_encoding="utf-8")

    # API Info
    API_TITLE: str = "Agent Management Platform API"
    API_VERSION: str = "1.0.0"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./agent_management.db")

    # Agents Directory
    AGENTS_DIR: str = os.getenv("AGENTS_DIR", "/app/.agents")

    # CORS - Production configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://frontend-75li8b5zx-travis-kennedys-projects.vercel.app",
        "https://frontend-nuxr624jz-travis-kennedys-projects.vercel.app",
        "https://*.vercel.app"
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "bdf7d62bd781987c78c9b36a59f1abdb90125ff2880aa3ed76014b077fac81d8")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
