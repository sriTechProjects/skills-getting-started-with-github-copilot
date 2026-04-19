"""
Comprehensive tests for Mergington High School API

Tests cover all endpoints with positive cases, edge cases, and error scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self):
        """Should return all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        # Verify expected activities exist
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_structure(self):
        """Should return activities with correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check first activity has all required fields
        first_activity = data["Chess Club"]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Should successfully sign up a student"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "test_student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test_student@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
    
    def test_signup_duplicate_fails(self):
        """Should fail when student already signed up"""
        email = "duplicate_test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Soccer Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self):
        """Should fail when activity doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_signup_missing_email_parameter(self):
        """Should fail when email parameter is missing"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_with_existing_participants(self):
        """Should successfully add new participant to activity with existing participants"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "new_participant@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "new_participant@mergington.edu" in chess_club["participants"]
    
    def test_signup_case_sensitive_email(self):
        """Should handle different case variations of email as different users"""
        email_lower = "casesensitive@mergington.edu"
        email_upper = "CASESENSITIVE@mergington.edu"
        
        # Both should be treated as different entries
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": email_lower}
        )
        response2 = client.post(
            "/activities/Art Club/signup",
            params={"email": email_upper}
        )
        
        # Both should succeed as they are different strings
        assert response1.status_code == 200
        assert response2.status_code == 200
    
    def test_signup_with_special_characters_in_email(self):
        """Should accept emails with special characters"""
        email = "user+test@mergington.edu"
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_success(self):
        """Should successfully unregister a student"""
        email = "unregister_test@mergington.edu"
        
        # First, signup
        client.post(
            "/activities/Debate Club/signup",
            params={"email": email}
        )
        
        # Then, unregister
        response = client.delete(
            "/activities/Debate Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Debate Club" in data["message"]
    
    def test_unregister_not_signed_up_fails(self):
        """Should fail when student is not signed up"""
        response = client.delete(
            "/activities/Science Club/signup",
            params={"email": "not_signed_up@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self):
        """Should fail when activity doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_unregister_missing_email_parameter(self):
        """Should fail when email parameter is missing"""
        response = client.delete("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_unregister_from_pre_populated_activity(self):
        """Should successfully unregister from activity with existing participants"""
        response = client.delete(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
    
    def test_cannot_unregister_twice(self):
        """Should fail when trying to unregister twice"""
        email = "double_unregister@mergington.edu"
        
        # Signup first
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        
        # Unregister once
        response1 = client.delete(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Try to unregister again - should fail
        response2 = client.delete(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 400


class TestRootRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_index(self):
        """Should redirect root path to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]
    
    def test_root_with_follow_redirects(self):
        """Should successfully reach index.html following redirect"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200


class TestSignupSignoutFlow:
    """Integration tests for signup/unregister flow"""
    
    def test_full_signup_and_unregister_flow(self):
        """Should handle full flow: signup, verify, then unregister"""
        email = "flow_test@mergington.edu"
        activity = "Art Club"
        
        # Get initial state
        initial = client.get("/activities").json()
        initial_count = len(initial[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities").json()
        assert len(after_signup[activity]["participants"]) == initial_count + 1
        assert email in after_signup[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities").json()
        assert len(after_unregister[activity]["participants"]) == initial_count
        assert email not in after_unregister[activity]["participants"]
    
    def test_multiple_students_signup_same_activity(self):
        """Should allow multiple students to sign up for same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity = "Science Club"
        
        # Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity]["participants"]


class TestActivityNameHandling:
    """Tests for activity name handling in various cases"""
    
    def test_activity_name_case_sensitivity(self):
        """Should handle activity names with correct case"""
        # Correct case
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Different case should not find the activity
        response2 = client.post(
            "/activities/chess club/signup",
            params={"email": "test2@mergington.edu"}
        )
        assert response2.status_code == 404
    
    def test_activity_name_with_spaces(self):
        """Should properly handle activity names with spaces"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200