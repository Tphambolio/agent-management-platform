"""Integration tests for authentication endpoints"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestRegisterEndpoint:
    """Test user registration endpoint"""

    def test_register_success(self, client):
        """Test successful user registration"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "full_name": "New User"
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert data["username"] == "newuser"

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username fails"""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "SecurePass123"
        }

        # Register first user
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201

        # Try to register with same username
        user_data2 = {
            "username": "testuser",  # Same username
            "email": "test2@example.com",  # Different email
            "password": "SecurePass123"
        }

        response2 = client.post("/api/auth/register", json=user_data2)
        assert response2.status_code == 422

        data = response2.json()
        assert "error" in data
        assert "username" in data["error"].lower()

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email fails"""
        user_data = {
            "username": "testuser1",
            "email": "duplicate@example.com",
            "password": "SecurePass123"
        }

        # Register first user
        response1 = client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201

        # Try to register with same email
        user_data2 = {
            "username": "testuser2",  # Different username
            "email": "duplicate@example.com",  # Same email
            "password": "SecurePass123"
        }

        response2 = client.post("/api/auth/register", json=user_data2)
        assert response2.status_code == 422

        data = response2.json()
        assert "error" in data
        assert "email" in data["error"].lower()

    def test_register_weak_password(self, client):
        """Test registration with weak password fails"""
        user_data = {
            "username": "weakpass",
            "email": "weak@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422

        data = response.json()
        assert "error" in data

    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails"""
        user_data = {
            "username": "testuser",
            "email": "not-an-email",  # Invalid email format
            "password": "SecurePass123"
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_short_username(self, client):
        """Test registration with too short username fails"""
        user_data = {
            "username": "ab",  # Too short (< 3 chars)
            "email": "test@example.com",
            "password": "SecurePass123"
        }

        response = client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422


@pytest.mark.integration
class TestLoginEndpoint:
    """Test user login endpoint"""

    def test_login_success(self, client):
        """Test successful login"""
        # First register a user
        register_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "SecurePass123"
        }
        client.post("/api/auth/register", json=register_data)

        # Now login
        login_data = {
            "username": "loginuser",
            "password": "SecurePass123"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user_id" in data
        assert data["username"] == "loginuser"

    def test_login_wrong_password(self, client):
        """Test login with wrong password fails"""
        # Register a user
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123"
        }
        client.post("/api/auth/register", json=register_data)

        # Try to login with wrong password
        login_data = {
            "username": "testuser",
            "password": "WrongPassword123"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "error" in data

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user fails"""
        login_data = {
            "username": "nonexistent",
            "password": "SecurePass123"
        }

        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

        data = response.json()
        assert "error" in data


@pytest.mark.integration
class TestGetCurrentUserEndpoint:
    """Test get current user endpoint"""

    def test_get_current_user_success(self, client):
        """Test getting current user with valid token"""
        # Register and login
        register_data = {
            "username": "currentuser",
            "email": "current@example.com",
            "password": "SecurePass123",
            "full_name": "Current User"
        }
        client.post("/api/auth/register", json=register_data)

        login_data = {
            "username": "currentuser",
            "password": "SecurePass123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]

        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["username"] == "currentuser"
        assert data["email"] == "current@example.com"
        assert data["full_name"] == "Current User"
        assert data["is_active"] is True
        assert data["is_admin"] is False

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token fails"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # Forbidden without auth header

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token fails"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_get_current_user_malformed_token(self, client):
        """Test getting current user with malformed auth header fails"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        # Should fail because it expects "Bearer " prefix
        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow"""

    def test_complete_auth_flow(self, client):
        """Test complete flow: register -> login -> access protected endpoint"""
        # Step 1: Register
        register_data = {
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "FlowPass123",
            "full_name": "Flow User"
        }

        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        register_token = register_response.json()["access_token"]

        # Step 2: Login
        login_data = {
            "username": "flowuser",
            "password": "FlowPass123"
        }

        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]

        # Tokens should be different (new token issued on login)
        # Actually they might be the same if generated at same second with same data
        # So we just verify both work

        # Step 3: Access protected endpoint with register token
        me_response1 = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert me_response1.status_code == 200
        assert me_response1.json()["username"] == "flowuser"

        # Step 4: Access protected endpoint with login token
        me_response2 = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert me_response2.status_code == 200
        assert me_response2.json()["username"] == "flowuser"
