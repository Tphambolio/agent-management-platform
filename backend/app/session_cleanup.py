"""
Session Cleanup Utility
Handles stuck sessions and implements timeout logic
"""

from datetime import datetime, timedelta
from app.database import get_db
from app.models import Session, SessionStatus
from app.logging import get_logger

logger = get_logger(__name__)


def cleanup_stale_sessions(max_age_minutes: int = 30):
    """
    Mark sessions older than max_age_minutes as timed_out

    Args:
        max_age_minutes: Maximum age in minutes before timing out

    Returns:
        Number of sessions cleaned up
    """
    cutoff_time = datetime.utcnow() - timedelta(minutes=max_age_minutes)

    with get_db() as db:
        stale_sessions = db.query(Session).filter(
            Session.status == SessionStatus.IN_PROGRESS,
            Session.start_time < cutoff_time
        ).all()

        count = 0
        for session in stale_sessions:
            session.status = SessionStatus.FAILED
            session.end_time = datetime.utcnow()
            session.final_output = f"Session timed out after {max_age_minutes} minutes"

            if session.start_time:
                start = session.start_time.replace(tzinfo=None) if session.start_time.tzinfo else session.start_time
                end = session.end_time.replace(tzinfo=None) if session.end_time.tzinfo else session.end_time
                duration = (end - start).total_seconds()
                session.duration_seconds = int(duration)

            count += 1

        if count > 0:
            db.commit()
            logger.info(f"Cleaned up {count} stale session(s)")

        return count


def get_stale_sessions_count(max_age_minutes: int = 30):
    """Get count of stale sessions without modifying them"""
    cutoff_time = datetime.utcnow() - timedelta(minutes=max_age_minutes)

    with get_db() as db:
        count = db.query(Session).filter(
            Session.status == SessionStatus.IN_PROGRESS,
            Session.start_time < cutoff_time
        ).count()

        return count


if __name__ == "__main__":
    # CLI tool for manual cleanup
    import sys

    max_age = 30
    if len(sys.argv) > 1:
        try:
            max_age = int(sys.argv[1])
        except ValueError:
            print(f"Invalid max_age: {sys.argv[1]}, using default 30 minutes")

    print(f"Checking for sessions older than {max_age} minutes...")
    stale_count = get_stale_sessions_count(max_age)
    print(f"Found {stale_count} stale session(s)")

    if stale_count > 0:
        confirm = input("Clean up these sessions? (y/n): ")
        if confirm.lower() == 'y':
            cleaned = cleanup_stale_sessions(max_age)
            print(f"✅ Cleaned up {cleaned} session(s)")
        else:
            print("Cancelled")
    else:
        print("No stale sessions found")
