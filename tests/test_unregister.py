"""Tests for DELETE /activities/{activity_name}/signup endpoint"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for activity unregister/signup removal endpoint"""

    def test_unregister_success_removes_participant(self, client, fresh_activities):
        """
        Test: Successfully unregister a student from an activity
        AAA Pattern:
            Arrange: Choose activity with existing participant
            Act: DELETE request to remove participant
            Assert: Verify 200 status and participant removed from list
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email not in fresh_activities[activity_name]["participants"]
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_returns_success_message(self, client, fresh_activities):
        """
        Test: Unregister response includes success message with email and activity
        AAA Pattern:
            Arrange: Select enrolled participant
            Act: Send DELETE request
            Assert: Verify response message format
        """
        # Arrange
        email = "daniel@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client, fresh_activities):
        """
        Test: Unregister fails with 404 when activity doesn't exist
        AAA Pattern:
            Arrange: Use non-existent activity name
            Act: DELETE request
            Assert: Verify 404 status and error detail
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_non_enrolled_student_returns_400(self, client, fresh_activities):
        """
        Test: Cannot unregister student not enrolled in activity
        AAA Pattern:
            Arrange: Use email not in activity's participants
            Act: DELETE request
            Assert: Verify 400 status and error message
        """
        # Arrange
        email = "notsigned@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_then_resignup(self, client, fresh_activities):
        """
        Test: Student can re-signup after unregistering
        AAA Pattern:
            Arrange: Choose enrolled participant
            Act: Unregister, then signup again
            Assert: Both operations succeed and student is enrolled
        """
        # Arrange
        email = "emma@mergington.edu"
        activity_name = "Programming Class"

        # Act - Unregister
        response_delete = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert email not in fresh_activities[activity_name]["participants"]

        # Act - Re-signup
        response_post = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response_delete.status_code == 200
        assert response_post.status_code == 200
        assert email in fresh_activities[activity_name]["participants"]

    def test_unregister_from_empty_activity_returns_400(self, client, fresh_activities):
        """
        Test: Cannot unregister from activity with no participants
        AAA Pattern:
            Arrange: Select activity with no current participants (Tennis Club)
            Act: Try to unregister arbitrary email
            Assert: Verify 400 status
        """
        # Arrange
        email = "nobody@mergington.edu"
        activity_name = "Tennis Club"
        assert len(fresh_activities[activity_name]["participants"]) == 0

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_multiple_participants(self, client, fresh_activities):
        """
        Test: Can unregister multiple different students from same activity
        AAA Pattern:
            Arrange: Signup multiple emails, then define which to unregister
            Act: Unregister each one
            Assert: All are removed, others remain unaffected
        """
        # Arrange
        emails_to_add = [
            "student_a@mergington.edu",
            "student_b@mergington.edu",
            "student_c@mergington.edu"
        ]
        activity_name = "Drama Club"

        # First, signup all of them
        for email in emails_to_add:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )

        # Act - Unregister first two
        emails_to_remove = emails_to_add[:2]
        for email in emails_to_remove:
            response = client.delete(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert
        remaining = fresh_activities[activity_name]["participants"]
        for email in emails_to_remove:
            assert email not in remaining
        assert emails_to_add[2] in remaining

    def test_unregister_double_remove_fails(self, client, fresh_activities):
        """
        Test: Cannot unregister same student twice
        AAA Pattern:
            Arrange: Unregister once successfully
            Act: Try to unregister the same email again
            Assert: Second unregister returns 400
        """
        # Arrange
        email = "john@mergington.edu"
        activity_name = "Gym Class"

        # Act - First unregister (should succeed)
        response1 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Second unregister attempt (should fail)
        response2 = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"]
