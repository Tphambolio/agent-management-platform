"""Application configuration"""
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Agent Management Platform API"
    API_VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./agent_management.db"
    )
    
    # Agents Directory
    AGENTS_DIR: str = os.getenv(
        "AGENTS_DIR",
        "/home/rpas/wildfire-simulator-v2/.agents"
    )
    
    # CORS - Allow all for MVP
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
