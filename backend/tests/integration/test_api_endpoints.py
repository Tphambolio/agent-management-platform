"""Integration tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.integration
class TestAgentsEndpoints:
    """Test agent management endpoints"""

    def test_list_agents_empty(self, client):
        """Test listing agents when none exist"""
        response = client.get("/api/agents")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_list_agents_with_data(self, client, sample_agent):
        """Test listing agents when one exists"""
        response = client.get("/api/agents")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(agent["name"] == "Test Agent" for agent in data)

    def test_get_agent_by_id(self, client, sample_agent):
        """Test getting specific agent by ID"""
        response = client.get(f"/api/agents/{sample_agent.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_agent.id
        assert data["name"] == "Test Agent"

    def test_get_nonexistent_agent(self, client):
        """Test that getting nonexistent agent returns 404"""
        response = client.get("/api/agents/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestTasksEndpoints:
    """Test task management endpoints"""

    def test_create_task_success(self, client, sample_agent):
        """Test creating a valid task"""
        task_data = {
            "agent_id": sample_agent.id,
            "title": "Integration Test Task",
            "description": "This is a test task created during integration testing",
            "priority": 2
        }

        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["agent_id"] == sample_agent.id
        assert "id" in data

    def test_create_task_invalid_agent(self, client):
        """Test creating task with nonexistent agent fails"""
        task_data = {
            "agent_id": "00000000-0000-0000-0000-000000000000",
            "title": "Test Task",
            "description": "This is a test task description",
        }

        response = client.post("/api/tasks", json=task_data)
        # Should return 404 or 422 depending on validation
        assert response.status_code in [404, 422]

    def test_create_task_validation_error(self, client, sample_agent):
        """Test that invalid task data returns validation error"""
        task_data = {
            "agent_id": sample_agent.id,
            "title": "AB",  # Too short
            "description": "Short",  # Too short
        }

        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 422

        data = response.json()
        assert "error" in data
        assert data["error_code"] == "VALIDATION_ERROR"

    def test_list_tasks(self, client, sample_task):
        """Test listing tasks"""
        response = client.get("/api/tasks")
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 1
        assert any(task["title"] == "Test Task" for task in data)

    def test_get_task_by_id(self, client, sample_task):
        """Test getting specific task by ID"""
        response = client.get(f"/api/tasks/{sample_task.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == "Test Task"
