"""
Pytest configuration and fixtures for the FastAPI application tests.

This file provides:
- TestClient instance for making HTTP requests to the API
- Fresh copy of activities data for each test (test isolation)
- Fixtures for common test setup and teardown
"""

import pytest
import copy
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import app as app_module
from app import app


# Store reference to original activities for cleanup
ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture
def client():
    """
    Provide a TestClient instance for making HTTP requests to the API.
    
    The TestClient allows us to make requests to the FastAPI application
    without needing to run a live server.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of the activities database for each test.
    
    This fixture ensures test isolation by:
    - Creating a deep copy of the default activities data
    - Resetting the module's activities to this copy before each test
    - Cleaning up after the test
    
    This prevents tests from affecting each other's state.
    """
    # Create a deep copy of the original activities
    activities_copy = copy.deepcopy(ORIGINAL_ACTIVITIES)
    
    # Replace the module-level activities with our fresh copy
    app_module.activities = activities_copy
    
    yield activities_copy
    
    # Reset to original after test completes
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
