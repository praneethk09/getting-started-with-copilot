import pytest


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_redirect(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestActivitiesEndpoint:
    """Tests for GET /activities"""

    def test_get_all_activities_success(self, client):
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) > 0

    def test_get_activities_contains_required_fields(self, client):
        # Arrange & Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_data in activities.values():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_student(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister"""

    def test_unregister_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_not_registered(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestIntegrationFlow:
    """Integration tests for signup and unregister."""

    def test_signup_then_unregister(self, client):
        # Arrange
        activity_name = "Tennis Club"
        email = "integration@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200

        activities_response = client.get("/activities")
        participants_after = activities_response.json()[activity_name]["participants"]
        assert email not in participants_after
