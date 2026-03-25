"""Tests for POST /activities/{activity_name}/signup endpoint"""

import pytest


class TestSignupForActivity:
    """Test suite for activity signup endpoint"""

    def test_signup_success_adds_participant(self, client, fresh_activities):
        """
        Test: Successfully signup a student for an available activity
        AAA Pattern:
            Arrange: Define email and activity with available spot
            Act: POST request to signup endpoint
            Assert: Verify 200 status and participant added to activity
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Tennis Club"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_returns_success_message(self, client, fresh_activities):
        """
        Test: Signup response includes success message with email and activity name
        AAA Pattern:
            Arrange: Prepare request parameters
            Act: Send signup request
            Assert: Verify response message format
        """
        # Arrange
        email = "alice@mergington.edu"
        activity_name = "Art Studio"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Test: Signup fails with 404 when activity doesn't exist
        AAA Pattern:
            Arrange: Use non-existent activity name
            Act: POST signup request
            Assert: Verify 404 status and error detail
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_email_returns_400(self, client, fresh_activities):
        """
        Test: Cannot signup same email twice for same activity
        AAA Pattern:
            Arrange: Get already-enrolled student email
            Act: Attempt signup with that email
            Assert: Verify 400 status and "already signed up" error
        """
        # Arrange
        # Michael is already in Chess Club
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "Already signed up" in response.json()["detail"]

    def test_signup_same_email_different_activities(self, client, fresh_activities):
        """
        Test: Same student can signup for multiple different activities
        AAA Pattern:
            Arrange: Use same email for two different activities
            Act: Signup for first, then second activity
            Assert: Both signups succeed and email appears in both lists
        """
        # Arrange
        email = "multiclass@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Art Studio"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )

        # Act - Second signup
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in fresh_activities[activity1]["participants"]
        assert email in fresh_activities[activity2]["participants"]

    def test_signup_to_empty_activity(self, client, fresh_activities):
        """
        Test: Can signup to activity with no current participants
        AAA Pattern:
            Arrange: Identify empty activity (Tennis Club starts empty)
            Act: Signup new participant
            Assert: Participant added successfully and count is 1
        """
        # Arrange
        email = "tennis_fan@mergington.edu"
        activity_name = "Tennis Club"
        assert len(fresh_activities[activity_name]["participants"]) == 0

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(fresh_activities[activity_name]["participants"]) == 1
        assert email in fresh_activities[activity_name]["participants"]

    def test_signup_multiple_participants_to_same_activity(self, client, fresh_activities):
        """
        Test: Multiple different students can signup for the same activity
        AAA Pattern:
            Arrange: Define multiple emails
            Act: Signup each email consecutively
            Assert: All are added to the activity's participant list
        """
        # Arrange
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity_name = "Robotics Club"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        participants = fresh_activities[activity_name]["participants"]
        assert len(participants) == initial_count + len(emails)
        for email in emails:
            assert email in participants
