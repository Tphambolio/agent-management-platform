#!/usr/bin/env python3
"""
Add the Architecture Analysis Report to the database so it appears in the frontend.
"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import get_db, engine
from backend.app.models import Report, Base

# Read the report content
with open('ARCHITECTURE_ANALYSIS_REPORT.md', 'r') as f:
    report_content = f.read()

# Extract summary from the report
summary = """Comprehensive architectural analysis of the agent-management-platform codebase.
Critical findings: Missing imports causing crashes, security vulnerabilities in JWT handling,
performance bottlenecks in database queries, WebSocket production readiness issues.
Includes 48-hour action plan and production readiness checklist."""

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create database session directly
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

try:
    # Create report entry
    report = Report(
        id=str(uuid.uuid4()),
        task_id="architecture-analysis-2025-11-18",
        agent_id="senior-architect-agent",
        project_id="agent-platform-production",
        title="Agent Management Platform - Architecture Analysis Report",
        content=report_content,
        format="markdown",
        summary=summary,
        tags=["architecture", "security", "performance", "production-readiness", "code-review"],
        meta={
            "analysis_date": "2025-11-18",
            "analyst": "Claude Code + Agent Team",
            "scope": "Full Stack (Backend + Frontend)",
            "critical_issues": 3,
            "high_priority_issues": 8,
            "medium_priority_issues": 12,
            "lines_analyzed": 5000,
            "estimated_fix_time_hours": 50
        }
    )

    db.add(report)
    db.commit()

    print(f"✅ Report added successfully!")
    print(f"Report ID: {report.id}")
    print(f"Title: {report.title}")
    print(f"Tags: {', '.join(report.tags)}")
    print(f"\nThe report is now visible in your frontend at /reports")

except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    raise
finally:
    db.close()
