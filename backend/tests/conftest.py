"""Pytest configuration and shared fixtures"""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import Agent, Task, Project, User, AgentStatus, TaskStatus


# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Create test database engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)
        # Remove test database file
        if os.path.exists("./test.db"):
            os.remove("./test.db")


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_agent(test_db):
    """Create a sample agent for testing"""
    agent = Agent(
        id="test-agent-123",
        name="Test Agent",
        type="research",
        specialization="Testing",
        capabilities=["testing", "validation"],
        status=AgentStatus.IDLE
    )
    test_db.add(agent)
    test_db.commit()
    test_db.refresh(agent)
    return agent


@pytest.fixture
def sample_project(test_db):
    """Create a sample project for testing"""
    project = Project(
        id="test-project-123",
        name="Test Project",
        description="A project for testing",
        repository_path="/test/path"
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


@pytest.fixture
def sample_task(test_db, sample_agent, sample_project):
    """Create a sample task for testing"""
    task = Task(
        id="test-task-123",
        agent_id=sample_agent.id,
        project_id=sample_project.id,
        title="Test Task",
        description="This is a test task for validation",
        status=TaskStatus.PENDING,
        priority=2,
        context={"test": "data"}
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    return task
