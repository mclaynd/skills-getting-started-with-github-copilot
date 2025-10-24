"""
Test suite for Mergington High School Activities API

Comprehensive tests for the FastAPI application endpoints using pytest.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test to ensure clean state."""
    original_activities = activities.copy()
    # Reset to original state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team for training and matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Swimming Club": {
            "description": "Practice swimming techniques and compete in meets",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": []
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture with peers",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        }
    })
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successfully retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        
        # Check that all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Swimming Club", "Drama Club", "Art Workshop", "Math Olympiad", "Debate Club"
        ]
        for activity in expected_activities:
            assert activity in data
            
    def test_get_activities_structure(self, client, reset_activities):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Test Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Test the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successfully signing up for an activity."""
        response = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Signed up test@mergington.edu for Soccer Team"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signup is prevented."""
        # First signup should succeed
        response1 = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student is already signed up"
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup when activity is at capacity."""
        # Fill Math Olympiad to capacity (10 participants)
        for i in range(10):
            email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/Math Olympiad/signup?email={email}")
            assert response.status_code == 200
        
        # Try to add one more participant
        response = client.post("/activities/Math Olympiad/signup?email=overflow@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name."""
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestUnregisterEndpoint:
    """Test the DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successfully unregistering from an activity."""
        # First sign up
        signup_response = client.post("/activities/Soccer Team/signup?email=test@mergington.edu")
        assert signup_response.status_code == 200
        
        # Then unregister
        response = client.delete("/activities/Soccer Team/unregister?email=test@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered test@mergington.edu from Soccer Team"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "test@mergington.edu" not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregistering when student is not registered."""
        response = client.delete("/activities/Soccer Team/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregistering from non-existent activity."""
        response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant."""
        # Unregister michael from Chess Club (he's already registered)
        response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
        # daniel should still be there
        assert "daniel@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Test integration scenarios with multiple operations."""
    
    def test_full_registration_cycle(self, client, reset_activities):
        """Test complete registration and unregistration cycle."""
        email = "fullcycle@mergington.edu"
        activity = "Drama Club"
        
        # Check initial state
        activities_response = client.get("/activities")
        initial_data = activities_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        after_signup_data = activities_response.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        final_data = activities_response.json()
        assert len(final_data[activity]["participants"]) == initial_count
        assert email not in final_data[activity]["participants"]
    
    def test_multiple_activities_same_student(self, client, reset_activities):
        """Test that a student can register for multiple activities."""
        email = "multistudent@mergington.edu"
        
        # Sign up for multiple activities
        activities_to_join = ["Soccer Team", "Drama Club", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in data[activity]["participants"]
    
    def test_capacity_management(self, client, reset_activities):
        """Test activity capacity management across multiple operations."""
        activity = "Math Olympiad"  # Has capacity of 10
        
        # Get initial participant count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()[activity]["participants"])
        
        # Fill to capacity
        emails = []
        for i in range(10 - initial_count):
            email = f"capacity{i}@mergington.edu"
            emails.append(email)
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Try to exceed capacity
        overflow_response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
        assert overflow_response.status_code == 400
        
        # Unregister one participant
        response = client.delete(f"/activities/{activity}/unregister?email={emails[0]}")
        assert response.status_code == 200
        
        # Now should be able to add one more
        response = client.post(f"/activities/{activity}/signup?email=newspot@mergington.edu")
        assert response.status_code == 200