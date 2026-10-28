import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activities_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Practice chess strategies",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Art Club": {
            "description": "Explore drawing and painting",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activities_data):
    with TestClient(app_module.app) as test_client:
        yield test_client