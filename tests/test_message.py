"""Tests for message/DM endpoints."""
import pytest
from fastapi.testclient import TestClient
import sys
import os
import uuid

# Get the absolute path to the project's root directory (one level up from the 'tests' folder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the project root to sys.path if it's not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app


client = TestClient(app)


def create_unique_user(username_suffix: str, email_suffix: str) -> dict:
    """Helper to create a unique user and return token and user data."""
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"user_{username_suffix}_{unique_id}",
        "email": f"user_{email_suffix}_{unique_id}@example.com",
        "password": "TestPass123!"
    }
    
    # Register
    client.post("/api/auth/register", json=user_data)
    
    # Login to get token
    login_response = client.post(
        "/api/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    
    if login_response.status_code != 200:
        pytest.skip(f"Could not create test user: {login_response.json()}")
    
    token = login_response.json()["access_token"]
    
    return {
        "username": user_data["username"],
        "email": user_data["email"],
        "token": token
    }


@pytest.fixture(scope="function")
def sender():
    """Create a sender user."""
    return create_unique_user("sender", "sender")


@pytest.fixture(scope="function")
def receiver():
    """Create a receiver user."""
    return create_unique_user("receiver", "receiver")


class TestMessageEndpoints:
    """Test message endpoints functionality."""
    
    def test_send_message_to_nonexistent_user(self, sender: dict):
        """Test sending to a user that doesn't exist."""
        response = client.post(
            "/api/messages/",
            json={
                "receiver_id": 99999,
                "content": "Hello!"
            },
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        assert response.status_code == 404
    
    def test_send_message_to_nonexistent_user(self, sender: dict):
        """Test sending to a user that doesn't exist."""
        response = client.post(
            "/api/messages/",
            json={
                "receiver_id": 99999,
                "content": "Hello!"
            },
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        # Returns 400 when receiver doesn't exist
        assert response.status_code == 400
    
    def test_send_message_unauthorized(self):
        """Test sending without authorization."""
        response = client.post(
            "/api/messages/",
            json={
                "receiver_id": 2,
                "content": "Hello!"
            }
        )
        # Returns 401 Unauthorized without token
        assert response.status_code == 401
    
    def test_list_messages_success(self, sender: dict):
        """Test listing messages returns valid response."""
        response = client.get(
            "/api/messages/",
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_messages_unauthorized(self):
        """Test listing without authorization."""
        response = client.get("/api/messages/")
        # Returns 401 Unauthorized without token
        assert response.status_code == 401
    
    def test_get_conversation_with_nonexistent_user(self, sender: dict):
        """Test conversation with user that doesn't exist."""
        response = client.get(
            "/api/messages/99999",
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        # Returns 400 when other user doesn't exist
        assert response.status_code == 400
    
    def test_get_conversation_unauthorized(self):
        """Test getting conversation without authorization."""
        response = client.get("/api/messages/1")
        # Returns 401 Unauthorized without token
        assert response.status_code == 401
    
    def test_mark_nonexistent_message_as_read(self, sender: dict):
        """Test marking non-existent message as read."""
        response = client.put(
            "/api/messages/99999/read",
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        assert response.status_code == 404
    
    def test_mark_as_read_unauthorized(self):
        """Test mark as read without authorization."""
        response = client.put("/api/messages/1/read")
        # Returns 401 Unauthorized without token
        assert response.status_code == 401
    
    def test_delete_nonexistent_message(self, sender: dict):
        """Test deleting non-existent message."""
        response = client.delete(
            "/api/messages/99999",
            headers={"Authorization": f"Bearer {sender['token']}"}
        )
        assert response.status_code == 404
    
    def test_delete_unauthorized(self):
        """Test delete without authorization."""
        response = client.delete("/api/messages/1")
        # Returns 401 Unauthorized without token
        assert response.status_code == 401

