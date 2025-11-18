"""Minimal FastAPI app for testing Render deployment"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Test imports one by one
print("Testing imports...")
try:
    from app.config import settings
    print(f"✅ config: API_TITLE={settings.API_TITLE}")
except Exception as e:
    print(f"❌ config failed: {e}")

try:
    from app.models import Agent
    print("✅ models")
except Exception as e:
    print(f"❌ models failed: {e}")

try:
    from app.database import init_db
    print("✅ database")
except Exception as e:
    print(f"❌ database failed: {e}")

app = FastAPI(
    title="Agent Management Platform API - Debug Test",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Minimal test app running",
        "status": "ok"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/test/db")
async def test_db():
    """Test database connection"""
    import os
    db_url = os.getenv("DATABASE_URL", "not set")

    # Fix postgres:// -> postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()

        return {
            "status": "connected",
            "database": "postgresql" if "postgresql" in db_url else "sqlite",
            "test_query": "ok"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "db_url_prefix": db_url[:30] if db_url != "not set" else "not set"
        }
