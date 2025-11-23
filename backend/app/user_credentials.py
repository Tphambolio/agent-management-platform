"""
User Credentials Management
Securely stores per-user API keys with encryption
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os
from cryptography.fernet import Fernet
import base64
from hashlib import sha256

Base = declarative_base()


class UserCredentials(Base):
    """Store encrypted API credentials per user"""
    __tablename__ = "user_credentials"

    user_id = Column(String, primary_key=True)
    anthropic_key_encrypted = Column(Text, nullable=True)
    gemini_key_encrypted = Column(Text, nullable=True)
    brave_key_encrypted = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CredentialsManager:
    """Manage encrypted user credentials"""

    def __init__(self):
        # Get encryption key from environment or generate
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            # Generate from a secret (in production, use a real secret)
            secret = os.getenv("SECRET_KEY", "default-secret-change-in-production")
            key_bytes = sha256(secret.encode()).digest()
            encryption_key = base64.urlsafe_b64encode(key_bytes)

        self.cipher = Fernet(encryption_key)

    def encrypt(self, value: str) -> str:
        """Encrypt a string value"""
        if not value:
            return None
        return self.cipher.encrypt(value.encode()).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """Decrypt a string value"""
        if not encrypted_value:
            return None
        return self.cipher.decrypt(encrypted_value.encode()).decode()

    def store_credentials(self, db, user_id: str,
                         anthropic_key: str = None,
                         gemini_key: str = None,
                         brave_key: str = None):
        """Store encrypted credentials for a user"""
        creds = db.query(UserCredentials).filter(
            UserCredentials.user_id == user_id
        ).first()

        if not creds:
            creds = UserCredentials(user_id=user_id)
            db.add(creds)

        if anthropic_key:
            creds.anthropic_key_encrypted = self.encrypt(anthropic_key)
        if gemini_key:
            creds.gemini_key_encrypted = self.encrypt(gemini_key)
        if brave_key:
            creds.brave_key_encrypted = self.encrypt(brave_key)

        creds.updated_at = datetime.utcnow()
        db.commit()

        return creds

    def get_credentials(self, db, user_id: str) -> dict:
        """Get decrypted credentials for a user"""
        creds = db.query(UserCredentials).filter(
            UserCredentials.user_id == user_id
        ).first()

        if not creds:
            return {
                "anthropic_key": None,
                "gemini_key": None,
                "brave_key": None
            }

        return {
            "anthropic_key": self.decrypt(creds.anthropic_key_encrypted),
            "gemini_key": self.decrypt(creds.gemini_key_encrypted),
            "brave_key": self.decrypt(creds.brave_key_encrypted)
        }

    def has_credentials(self, db, user_id: str) -> bool:
        """Check if user has stored credentials"""
        creds = db.query(UserCredentials).filter(
            UserCredentials.user_id == user_id
        ).first()

        return bool(creds and creds.anthropic_key_encrypted)


# Singleton instance
credentials_manager = CredentialsManager()
