"""
Integration tests for the FastAPI application endpoints.

These tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Make HTTP request to the endpoint
- Assert: Verify the response status code, data, and side effects

Tests cover all endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- POST /activities/{activity_name}/unregister
- GET / (root redirect)
"""

import pytest


@pytest.mark.integration
class TestGetActivities:
    """Test the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, fresh_activities):
        """
        Arrange: Client and fresh activities database
        Act: GET request to /activities endpoint
        Assert: Response contains all activities with correct structure
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class", "Debate Team", "Science Club"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert set(activities.keys()) == set(expected_activities)

    def test_get_activities_includes_participant_details(self, client, fresh_activities):
        """
        Arrange: Chess Club has participants
        Act: GET request to /activities endpoint
        Assert: Response includes description, schedule, capacity, and participant list
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        activity = activities[activity_name]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_returns_correct_participant_count(self, client, fresh_activities):
        """
        Arrange: Chess Club with 2 participants
        Act: GET request to /activities endpoint
        Assert: Response shows correct participant count
        """
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        participants = activities[activity_name]["participants"]
        
        assert len(participants) == 2
        assert "michael@mergington.edu" in participants
        assert "daniel@mergington.edu" in participants


@pytest.mark.integration
class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, fresh_activities):
        """
        Arrange: New student email and valid activity name
        Act: POST signup request
        Assert: Response is successful and student is added
        """
        # Arrange
        activity_name = "Debate Team"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert email in fresh_activities[activity_name]["participants"]

    def test_signup_duplicate_error(self, client, fresh_activities):
        """
        Arrange: Student already signed up for Chess Club
        Act: Attempt to signup again for same activity
        Assert: Response is 400 error with duplicate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client, fresh_activities):
        """
        Arrange: Non-existent activity name
        Act: POST signup request for invalid activity
        Assert: Response is 404 not found error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_updates_participant_count(self, client, fresh_activities):
        """
        Arrange: Science Club with 0 participants
        Act: New student signs up
        Assert: Participant count increases
        """
        # Arrange
        activity_name = "Science Club"
        email = "scientist@mergington.edu"
        count_before = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        count_after = len(fresh_activities[activity_name]["participants"])
        assert count_after == count_before + 1


@pytest.mark.integration
class TestUnregisterEndpoint:
    """Test the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, fresh_activities):
        """
        Arrange: Student signed up for Chess Club
        Act: POST unregister request
        Assert: Response is successful and student is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert email not in fresh_activities[activity_name]["participants"]

    def test_unregister_not_participant_error(self, client, fresh_activities):
        """
        Arrange: Student NOT signed up for this activity
        Act: Attempt to unregister non-participant
        Assert: Response is 400 error with not signed up message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "notasignup@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client, fresh_activities):
        """
        Arrange: Non-existent activity name
        Act: POST unregister request for invalid activity
        Assert: Response is 404 not found error
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_updates_participant_count(self, client, fresh_activities):
        """
        Arrange: Chess Club with 2 participants
        Act: One student unregisters
        Assert: Participant count decreases
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        count_before = len(fresh_activities[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        count_after = len(fresh_activities[activity_name]["participants"])
        assert count_after == count_before - 1

    def test_unregister_frees_capacity(self, client, fresh_activities):
        """
        Arrange: Chess Club with 2 participants out of 12 capacity
        Act: One student unregisters
        Assert: Available spots increase
        """
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        activity = fresh_activities[activity_name]
        spots_before = activity["max_participants"] - len(activity["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        spots_after = activity["max_participants"] - len(activity["participants"])
        assert spots_after == spots_before + 1


@pytest.mark.integration
class TestRootEndpoint:
    """Test the GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Client ready for request
        Act: GET request to root endpoint
        Assert: Redirect response to /static/index.html
        """
        # Arrange
        # (no setup needed for this test)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_with_follow(self, client):
        """
        Arrange: Client ready for request
        Act: GET request to root endpoint with redirect following
        Assert: Final response is from index.html (HTML content)
        """
        # Arrange
        # (no setup needed for this test)

        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
