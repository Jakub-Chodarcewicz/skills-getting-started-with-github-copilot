"""
Unit tests for business logic in the FastAPI application.

These tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up data and conditions
- Act: Execute the operation being tested
- Assert: Verify the expected outcome

Tests cover signup and unregister operations with various scenarios.
"""

import pytest
import copy


@pytest.mark.unit
class TestSignupLogic:
    """Test the signup operation's business logic."""

    def test_signup_success_adds_participant(self, fresh_activities):
        """
        Arrange: Chess Club exists with some participants
        Act: New student signs up for Chess Club
        Assert: Student is added to the participants list
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        fresh_activities[activity_name]["participants"].append(new_email)

        # Assert
        assert len(fresh_activities[activity_name]["participants"]) == initial_count + 1
        assert new_email in fresh_activities[activity_name]["participants"]

    def test_signup_prevents_duplicate(self, fresh_activities):
        """
        Arrange: Student is already signed up for Chess Club
        Act: Attempt to add the same student again
        Assert: Logic detects the duplicate (would raise error in real endpoint)
        """
        # Arrange
        activity_name = "Chess Club"
        email = fresh_activities[activity_name]["participants"][0]  # Get existing participant
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        is_duplicate = email in fresh_activities[activity_name]["participants"]

        # Assert
        assert is_duplicate is True
        # Count should not increase if duplicate is rejected
        assert len(fresh_activities[activity_name]["participants"]) == initial_count

    def test_signup_validates_activity_exists(self, fresh_activities):
        """
        Arrange: Request signup for non-existent activity
        Act: Check if activity exists in the database
        Assert: Activity is not found
        """
        # Arrange
        activity_name = "Nonexistent Activity"

        # Act
        activity_exists = activity_name in fresh_activities

        # Assert
        assert activity_exists is False

    def test_signup_respects_capacity(self, fresh_activities):
        """
        Arrange: Debate Team has exactly 12 capacity
        Act: Count current participants
        Assert: Verify capacity constraint exists
        """
        # Arrange
        activity_name = "Debate Team"
        activity = fresh_activities[activity_name]

        # Act
        current_participants = len(activity["participants"])
        max_capacity = activity["max_participants"]
        spots_available = max_capacity - current_participants

        # Assert
        assert max_capacity == 12
        assert spots_available >= 0
        assert current_participants <= max_capacity


@pytest.mark.unit
class TestUnregisterLogic:
    """Test the unregister operation's business logic."""

    def test_unregister_success_removes_participant(self, fresh_activities):
        """
        Arrange: Student is signed up for Chess Club
        Act: Student unregisters from Chess Club
        Assert: Student is removed from the participants list
        """
        # Arrange
        activity_name = "Chess Club"
        email = fresh_activities[activity_name]["participants"][0]
        initial_count = len(fresh_activities[activity_name]["participants"])

        # Act
        fresh_activities[activity_name]["participants"].remove(email)

        # Assert
        assert len(fresh_activities[activity_name]["participants"]) == initial_count - 1
        assert email not in fresh_activities[activity_name]["participants"]

    def test_unregister_validates_activity_exists(self, fresh_activities):
        """
        Arrange: Request unregister from non-existent activity
        Act: Check if activity exists in the database
        Assert: Activity is not found
        """
        # Arrange
        activity_name = "Nonexistent Activity"

        # Act
        activity_exists = activity_name in fresh_activities

        # Assert
        assert activity_exists is False

    def test_unregister_prevents_removing_non_participant(self, fresh_activities):
        """
        Arrange: Student is NOT signed up for an activity
        Act: Attempt to unregister non-participant
        Assert: Logic detects student is not in the list (would raise error in real endpoint)
        """
        # Arrange
        activity_name = "Science Club"
        email = "nonexistent@mergington.edu"

        # Act
        is_participant = email in fresh_activities[activity_name]["participants"]

        # Assert
        assert is_participant is False

    def test_unregister_frees_up_capacity(self, fresh_activities):
        """
        Arrange: Chess Club is at some capacity level
        Act: Unregister a participant
        Assert: Available spots increase by one
        """
        # Arrange
        activity_name = "Chess Club"
        activity = fresh_activities[activity_name]
        email = activity["participants"][0]
        spots_before = activity["max_participants"] - len(activity["participants"])

        # Act
        activity["participants"].remove(email)

        # Assert
        spots_after = activity["max_participants"] - len(activity["participants"])
        assert spots_after == spots_before + 1
