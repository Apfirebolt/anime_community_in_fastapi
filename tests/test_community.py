import os
import sys
import uuid

from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app

client = TestClient(app)


def get_auth_token():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data.get("access_token") or data.get("token")


def test_create_community_unauthorized():
    response = client.post(
        "/api/community/",
        json={"name": "Unauthorized Community", "description": "No token", "anime": "Naruto"},
    )
    assert response.status_code == 401


def test_create_community_with_token():
    token = get_auth_token()
    name = f"TestCommunity-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/community/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": "A test community", "anime": "One Piece"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == name
    assert data["description"] == "A test community"
    assert data["anime"] == "One Piece"
    assert "id" in data
    assert "creator_id" in data


def test_list_communities_with_token():
    token = get_auth_token()
    response = client.get(
        "/api/community/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "description" in item
        assert "anime" in item
        assert "creator_id" in item
