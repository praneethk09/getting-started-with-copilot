import pytest
from copy import deepcopy
from starlette.testclient import TestClient

from src import app as api_app
from src.app import app, activities as _initial_activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: reset in-memory activity state before each test
    api_app.activities = deepcopy(_initial_activities)
    yield


@pytest.fixture
def client():
    """Fixture providing TestClient for FastAPI app"""
    return TestClient(app)
