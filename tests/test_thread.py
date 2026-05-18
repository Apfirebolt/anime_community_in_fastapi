import os
import sys
import uuid
import asyncio

from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app

from backend.db import auth_db

client = TestClient(app)


def get_auth_token():
    response = client.post(
        "/api/auth/login", json={"email": "ash@gmail.com", "password": "pass123"}
    )
    assert response.status_code == 200
    data = response.json()
    return data.get("access_token") or data.get("token")


def get_auth_token_for(email: str, password: str):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    return data.get("access_token") or data.get("token")


def create_community(token: str):
    name = f"ThreadTestCommunity-{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/api/community/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": "Community for thread tests", "anime": "My Hero Academia"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def get_user_id_by_email(email: str) -> int:
    user = asyncio.run(auth_db.get_user_by_email(email))
    assert user is not None
    return user.id


def test_create_thread_unauthorized():
    response = client.post(
        "/api/community/1/threads",
        json={"title": "Unauthorized Thread", "description": "No token"},
    )
    assert response.status_code == 401


def test_create_and_read_thread_with_token():
    token = get_auth_token()
    community = create_community(token)

    response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "My First Thread", "description": "Thread description"},
    )
    assert response.status_code == 201, response.text
    thread = response.json()

    assert thread["title"] == "My First Thread"
    assert thread["description"] == "Thread description"
    assert thread["community_id"] == community["id"]
    assert thread["creator_id"] == community["creator_id"]
    assert thread["id"]

    # Retrieve by thread id
    response = client.get(f"/api/community/threads/{thread['id']}")
    assert response.status_code == 200
    fetched = response.json()
    assert fetched["id"] == thread["id"]
    assert fetched["title"] == thread["title"]


def test_list_threads_for_community():
    token = get_auth_token()
    community = create_community(token)

    response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Community Thread", "description": "Listable thread"},
    )
    assert response.status_code == 201, response.text
    thread = response.json()

    response = client.get(f"/api/community/{community['id']}/threads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(item["id"] == thread["id"] for item in data)


def test_update_thread_by_creator():
    token = get_auth_token()
    community = create_community(token)
    response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updatable Thread", "description": "Initial description"},
    )
    assert response.status_code == 201, response.text
    thread = response.json()

    response = client.put(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Updated Title", "description": "Updated description"},
    )
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Updated description"
    assert updated["id"] == thread["id"]


def test_delete_thread_by_creator():
    token = get_auth_token()
    community = create_community(token)
    response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Deletable Thread", "description": "Delete me"},
    )
    assert response.status_code == 201, response.text
    thread = response.json()

    response = client.delete(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204

    response = client.get(f"/api/community/threads/{thread['id']}")
    assert response.status_code == 404


def test_update_delete_thread_forbidden_for_other_user():
    creator_token = get_auth_token()
    other_token = get_auth_token_for("test@example.com", "testpassword")
    community = create_community(creator_token)
    response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={"title": "Protected Thread", "description": "Owner only"},
    )
    assert response.status_code == 201, response.text
    thread = response.json()

    response = client.put(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"title": "Malicious Update"},
    )
    assert response.status_code == 403

    response = client.delete(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 403


def test_assign_moderator_by_creator():
    creator_token = get_auth_token()
    community = create_community(creator_token)

    moderator_id = get_user_id_by_email("test@example.com")

    response = client.post(
        f"/api/community/{community['id']}/moderators",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={"user_id": moderator_id},
    )
    assert response.status_code == 201, response.text
    moderator = response.json()
    assert moderator["community_id"] == community["id"]
    assert moderator["user_id"] == moderator_id

    response = client.get(f"/api/community/{community['id']}/moderators")
    assert response.status_code == 200
    moderators = response.json()
    assert any(item["id"] == moderator["id"] for item in moderators)


def test_assigned_moderator_can_manage_thread():
    creator_token = get_auth_token()
    moderator_token = get_auth_token_for("test@example.com", "testpassword")
    community = create_community(creator_token)

    moderator_id = get_user_id_by_email("test@example.com")

    response = client.post(
        f"/api/community/{community['id']}/moderators",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={"user_id": moderator_id},
    )
    assert response.status_code == 201, response.text

    thread_response = client.post(
        f"/api/community/{community['id']}/threads",
        headers={"Authorization": f"Bearer {creator_token}"},
        json={"title": "Moderator Thread", "description": "Moderation test"},
    )
    assert thread_response.status_code == 201, thread_response.text
    thread = thread_response.json()

    update_response = client.put(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {moderator_token}"},
        json={"title": "Moderator Updated Thread"},
    )
    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["title"] == "Moderator Updated Thread"

    delete_response = client.delete(
        f"/api/community/threads/{thread['id']}",
        headers={"Authorization": f"Bearer {moderator_token}"},
    )
    assert delete_response.status_code == 204

    confirm_response = client.get(f"/api/community/threads/{thread['id']}")
    assert confirm_response.status_code == 404


def test_assign_moderator_forbidden_for_non_creator():
    creator_token = get_auth_token()
    other_token = get_auth_token_for("test@example.com", "testpassword")
    community = create_community(creator_token)

    moderator_id = get_user_id_by_email("test@example.com")

    response = client.post(
        f"/api/community/{community['id']}/moderators",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"user_id": moderator_id},
    )
    assert response.status_code == 403
