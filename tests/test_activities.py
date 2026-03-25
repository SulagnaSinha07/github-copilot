"""Tests for GET /activities endpoint - retrieve all activities"""

import pytest


class TestGetActivities:
    """Test suite for activities retrieval endpoint"""

    def test_get_activities_returns_success(self, client):
        """
        Test: GET /activities returns 200 status code
        AAA Pattern:
            Arrange: Use client fixture (already initialized)
            Act: Make GET request to /activities
            Assert: Verify status code is 200
        """
        # Arrange
        # (client fixture already provides initialized TestClient)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """
        Test: GET /activities returns activities as dictionary
        AAA Pattern:
            Arrange: Use client fixture
            Act: Make GET request and parse JSON
            Assert: Verify response is a dict with activity names as keys
        """
        # Arrange
        # (client fixture ready)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_all_required_fields(self, client):
        """
        Test: Each activity has required fields (description, schedule, max_participants, participants)
        AAA Pattern:
            Arrange: Make request to get activities
            Act: Inspect first activity structure
            Assert: Verify all required fields exist and have correct types
        """
        # Arrange
        # (client ready)

        # Act
        response = client.get("/activities")
        data = response.json()
        first_activity_name = list(data.keys())[0]
        first_activity = data[first_activity_name]

        # Assert
        required_fields = {"description", "schedule", "max_participants", "participants"}
        assert required_fields.issubset(set(first_activity.keys()))
        assert isinstance(first_activity["description"], str)
        assert isinstance(first_activity["schedule"], str)
        assert isinstance(first_activity["max_participants"], int)
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_contains_expected_activities(self, client):
        """
        Test: Response includes all initially defined activities
        AAA Pattern:
            Arrange: Expected activity list
            Act: Fetch activities from endpoint
            Assert: Verify all activities are present
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Tennis Club",
            "Basketball Team",
            "Drama Club",
            "Art Studio",
            "Science Club",
            "Robotics Club"
        ]

        # Act
        response = client.get("/activities")
        returned_activities = list(response.json().keys())

        # Assert
        for activity in expected_activities:
            assert activity in returned_activities

    def test_get_activities_initial_participants(self, client, fresh_activities):
        """
        Test: Activities have correct initial participant lists
        AAA Pattern:
            Arrange: Use fresh_activities fixture for clean state
            Act: Get activities and check specific participant lists
            Assert: Verify Chess Club and other populated activities have expected participants
        """
        # Arrange
        # (fresh_activities fixture ensures clean state)

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]

        # Programming Class should have 2 participants
        assert len(data["Programming Class"]["participants"]) == 2
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]

        # Tennis Club should start empty
        assert len(data["Tennis Club"]["participants"]) == 0
