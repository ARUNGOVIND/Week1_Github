import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_has_participants(self, client):
        """Test that activities include participants"""
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities["Chess Club"]
        
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Signup
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Basketball Team"]["participants"]
    
    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice for the same activity fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes the participant from the activity"""
        email = "michael@mergington.edu"
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test that unregistering a nonexistent participant fails"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test that unregister for nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_unregister(self, client):
        """Test signing up and then unregistering"""
        email = "integration@mergington.edu"
        activity = "Basketball Team"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
    
    def test_multiple_signups(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Science Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[activity]["participants"]
