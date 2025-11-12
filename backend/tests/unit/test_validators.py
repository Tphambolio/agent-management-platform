"""Unit tests for Pydantic validators"""
import pytest
from pydantic import ValidationError

from app.validators.schemas import (
    CreateTaskRequest,
    CreateAgentRequest,
    ResearchRequest
)


class TestCreateTaskRequest:
    """Test CreateTaskRequest validation"""

    def test_valid_task_request(self):
        """Test valid task request passes validation"""
        data = {
            "agent_id": "12345678-1234-1234-1234-123456789012",
            "title": "Test Task",
            "description": "This is a valid test task description with enough words",
            "priority": 3
        }
        request = CreateTaskRequest(**data)
        assert request.title == "Test Task"
        assert request.priority == 3

    def test_invalid_uuid(self):
        """Test that invalid UUID raises validation error"""
        data = {
            "agent_id": "not-a-uuid",
            "title": "Test Task",
            "description": "This is a test description",
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateTaskRequest(**data)

        errors = exc_info.value.errors()
        assert any("Must be a valid UUID" in str(error["msg"]) for error in errors)

    def test_title_too_short(self):
        """Test that short title raises validation error"""
        data = {
            "agent_id": "12345678-1234-1234-1234-123456789012",
            "title": "AB",  # Too short
            "description": "This is a test description with enough words",
        }
        with pytest.raises(ValidationError):
            CreateTaskRequest(**data)

    def test_description_too_few_words(self):
        """Test that description with too few words is rejected"""
        data = {
            "agent_id": "12345678-1234-1234-1234-123456789012",
            "title": "Test Task",
            "description": "Two words",  # Too few words
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateTaskRequest(**data)

        errors = exc_info.value.errors()
        assert any("at least 3 words" in str(error["msg"]) for error in errors)

    def test_priority_out_of_range(self):
        """Test that priority outside 1-5 range is rejected"""
        data = {
            "agent_id": "12345678-1234-1234-1234-123456789012",
            "title": "Test Task",
            "description": "This is a valid description",
            "priority": 10  # Out of range
        }
        with pytest.raises(ValidationError):
            CreateTaskRequest(**data)


class TestCreateAgentRequest:
    """Test CreateAgentRequest validation"""

    def test_valid_agent_request(self):
        """Test valid agent request passes validation"""
        data = {
            "name": "Test Agent",
            "type": "research",
            "specialization": "Testing and Validation",
            "capabilities": ["testing", "validation"]
        }
        request = CreateAgentRequest(**data)
        assert request.name == "Test Agent"
        assert len(request.capabilities) == 2

    def test_invalid_name_characters(self):
        """Test that invalid characters in name are rejected"""
        data = {
            "name": "Test@Agent!",  # Invalid characters
            "type": "research",
            "specialization": "Testing"
        }
        with pytest.raises(ValidationError) as exc_info:
            CreateAgentRequest(**data)

        errors = exc_info.value.errors()
        assert any("letters, numbers, spaces" in str(error["msg"]) for error in errors)

    def test_too_many_capabilities(self):
        """Test that too many capabilities are rejected"""
        data = {
            "name": "Test Agent",
            "type": "research",
            "specialization": "Testing",
            "capabilities": [f"capability_{i}" for i in range(25)]  # Too many
        }
        with pytest.raises(ValidationError):
            CreateAgentRequest(**data)
