"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

@pytest.fixture
def client():
    """Create a test client for the app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original_activities = {
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theatrical performances and acting workshops",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 14,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Math Club": {
            "description": "Advanced mathematics problems and competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu"]
        },
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
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert len(data) == 9
    
    def test_activity_structure(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_activity_has_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Basketball Team"]["participants"]) == 1
        assert "alex@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignup:
    """Test the /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_updates_participant_list(self, client):
        """Test that signup updates the participant list"""
        client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Basketball Team"]["participants"]
        assert len(data["Basketball Team"]["participants"]) == 2
    
    def test_signup_duplicate_participant(self, client):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Basketball Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test signing up for multiple activities"""
        email = "student@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups were successful
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball Team"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestUnregister:
    """Test the /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self, client):
        """Test unregistering a participant"""
        # First sign up
        client.post(
            "/activities/Basketball Team/signup?email=student@mergington.edu"
        )
        
        # Then unregister
        response = client.post(
            "/activities/Basketball Team/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "student@mergington.edu" in data["message"]
    
    def test_unregister_removes_from_list(self, client):
        """Test that unregister removes participant from list"""
        email = "student@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/Basketball Team/signup?email={email}"
        )
        
        # Unregister
        client.post(
            f"/activities/Basketball Team/unregister?email={email}"
        )
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball Team"]["participants"]
        assert len(data["Basketball Team"]["participants"]) == 1
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering someone not signed up"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notasignup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_original_participant(self, client):
        """Test unregistering an original participant"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert "alex@mergington.edu" not in data["Basketball Team"]["participants"]


class TestIntegration:
    """Integration tests"""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete signup and unregister flow"""
        email = "integration@mergington.edu"
        activity = "Drama Club"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        after_signup = len(response.json()[activity]["participants"])
        assert after_signup == initial_count + 1
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count
