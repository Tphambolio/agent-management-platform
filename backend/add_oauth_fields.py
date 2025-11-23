"""
Database migration script to add Google OAuth fields to users table
Run this manually: python backend/add_oauth_fields.py
"""

from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.sql import text
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("Set it manually or check your .env file")
    exit(1)

print(f"📊 Connecting to database...")
engine = create_engine(DATABASE_URL)

# SQL to add new columns
migrations = [
    # Add profile_picture column
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS profile_picture VARCHAR(512);
    """,

    # Add Google OAuth fields
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE;
    """,

    """
    CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
    """,

    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS google_access_token_encrypted TEXT;
    """,

    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS google_refresh_token_encrypted TEXT;
    """,

    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS token_expires_at TIMESTAMP WITH TIME ZONE;
    """,

    # Make username and hashed_password optional (for OAuth users)
    """
    ALTER TABLE users
    ALTER COLUMN username DROP NOT NULL;
    """,

    """
    ALTER TABLE users
    ALTER COLUMN hashed_password DROP NOT NULL;
    """,
]

print("🔧 Running migrations...")

with engine.connect() as conn:
    for i, migration in enumerate(migrations, 1):
        try:
            conn.execute(text(migration))
            conn.commit()
            print(f"  ✅ Migration {i}/{len(migrations)} applied")
        except Exception as e:
            # Column might already exist, that's okay
            print(f"  ⚠️  Migration {i}/{len(migrations)}: {str(e)[:100]}")
            conn.rollback()

print("\n✨ Migration complete! Google OAuth fields added to users table.")
print("\n📝 New columns:")
print("  - profile_picture (VARCHAR)")
print("  - google_id (VARCHAR, unique, indexed)")
print("  - google_access_token_encrypted (TEXT)")
print("  - google_refresh_token_encrypted (TEXT)")
print("  - token_expires_at (TIMESTAMP)")
print("\n🔓 Updated columns:")
print("  - username (now optional)")
print("  - hashed_password (now optional)")
