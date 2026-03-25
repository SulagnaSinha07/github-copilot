"""Pytest configuration and shared fixtures for FastAPI tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture: Provides a TestClient for making HTTP requests to the FastAPI app.
    Ensures a fresh app instance for each test.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Fixture: Provides a fresh copy of activities for each test.
    Resets app.activities to initial state to avoid test interdependence.
    
    Note: This fixture modifies the app's global activities dict.
    In a production app, you'd want to use dependency injection to isolate state.
    """
    from src.app import activities
    
    # Store original state
    original_state = {
        key: {
            "description": act["description"],
            "schedule": act["schedule"],
            "max_participants": act["max_participants"],
            "participants": act["participants"].copy()
        }
        for key, act in activities.items()
    }
    
    yield activities
    
    # Restore original state after test
    for key in activities:
        activities[key]["participants"] = original_state[key]["participants"].copy()
