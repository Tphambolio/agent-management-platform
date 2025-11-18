"""Unit tests for authentication and JWT handling"""
import pytest
from datetime import timedelta
from jose import jwt, JWTError

from app.auth.jwt_handler import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    SECRET_KEY,
    ALGORITHM
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password(self):
        """Test that password is hashed correctly"""
        password = "SecurePassword123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "SecurePassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "SecurePassword123"
        wrong_password = "WrongPassword123"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)"""
        password = "SecurePassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestJWTTokens:
    """Test JWT token creation and verification"""

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {
            "user_id": "123",
            "username": "testuser",
            "email": "test@example.com"
        }

        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test JWT token decoding"""
        data = {
            "user_id": "123",
            "username": "testuser",
            "email": "test@example.com"
        }

        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded["user_id"] == "123"
        assert decoded["username"] == "testuser"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded  # Expiration time should be present

    def test_create_token_with_custom_expiry(self):
        """Test token creation with custom expiration"""
        data = {"user_id": "123"}
        expires_delta = timedelta(minutes=5)

        token = create_access_token(data, expires_delta=expires_delta)
        decoded = decode_access_token(token)

        assert "exp" in decoded
        assert decoded["user_id"] == "123"

    def test_decode_invalid_token(self):
        """Test that decoding invalid token raises error"""
        from fastapi import HTTPException

        invalid_token = "invalid.token.here"

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(invalid_token)

        assert exc_info.value.status_code == 401

    def test_decode_expired_token(self):
        """Test that decoding expired token raises error"""
        from fastapi import HTTPException

        data = {"user_id": "123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-10)
        token = create_access_token(data, expires_delta=expires_delta)

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)

        assert exc_info.value.status_code == 401

    def test_token_contains_all_data(self):
        """Test that token contains all provided data"""
        data = {
            "user_id": "user-123",
            "username": "john_doe",
            "email": "john@example.com",
            "custom_field": "custom_value"
        }

        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded["user_id"] == data["user_id"]
        assert decoded["username"] == data["username"]
        assert decoded["email"] == data["email"]
        assert decoded["custom_field"] == data["custom_field"]
