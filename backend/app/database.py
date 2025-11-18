"""Database setup and session management"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from .models import Base

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL, use SQLite
if not DATABASE_URL:
    print("⚠️  DATABASE_URL not set, using SQLite")
    DATABASE_URL = "sqlite:///./agent_management.db"

# Fix Render PostgreSQL URL (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    print(f"Converting postgres:// to postgresql:// for SQLAlchemy 2.0 compatibility")
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print(f"Database: {DATABASE_URL[:50]}...")

# Create engine
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
        echo=False
    )
    print("✅ Database engine created successfully")
except Exception as e:
    print(f"❌ Database engine creation failed: {e}")
    print("⚠️  Falling back to SQLite")
    # Fallback to SQLite if PostgreSQL connection fails
    DATABASE_URL = "sqlite:///./agent_management.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    print("✅ Fallback SQLite engine created")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database by creating all tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Session:
    """Get database session context manager"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get database session (for synchronous use)"""
    return SessionLocal()
