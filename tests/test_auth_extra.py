import os
import sys
import uuid
import bcrypt
import pytest
import asyncio
from fastapi import HTTPException

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.auth import hashing, jwt, models, services
from backend.auth.schema import TokenData
from backend.auth_db import create_user as create_user_top
from backend.db.auth_db import create_user as create_user_db, get_user_by_email as get_user_by_email_db, get_user_by_id as get_user_by_id_db, update_user_password as update_user_password_db, get_all_users as get_all_users_db


def test_password_hashing_and_legacy_bcrypt_fallback():
    password = "MySecret123!"
    hashed = hashing.get_password_hash(password)
    assert hashing.verify_password(password, hashed)

    # legacy bcrypt support for backward compatibility
    legacy_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    assert hashing.verify_password(password, legacy_hash)
    assert hashing.is_legacy_bcrypt_hash(legacy_hash)
    assert not hashing.is_legacy_bcrypt_hash("not_a_hash")


def test_jwt_create_and_verify_token():
    data = {"sub": "john@example.com", "id": 42}
    token = jwt.create_access_token(data)
    assert isinstance(token, str)
    token_data = jwt.verify_token(token, HTTPException(status_code=401, detail="Invalid"))
    assert isinstance(token_data, TokenData)
    assert token_data.email == "john@example.com"
    assert token_data.id == 42


def test_jwt_invalid_token_raises():
    invalid_token = "bad.token.value"
    with pytest.raises(jwt.HTTPException):
        jwt.verify_token(invalid_token, jwt.HTTPException(status_code=401, detail="Invalid"))


def test_user_model_password_check():
    user = models.User(username="user1", email="user1@example.com", role="user", password="secret")
    assert user.check_password("secret")
    assert not user.check_password("wrong")


def test_auth_services_register_and_profile():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    request = models.User(username="serviceuser", email=email, role="user", password="servicepass")
    # Use async service layer functions via asyncio.run
    result = asyncio.run(services.new_user_register(request))
    assert result is not None
    assert result.email == email
    assert result.username == "serviceuser"

    all_users = asyncio.run(services.all_users())
    assert isinstance(all_users, list)
    assert any(user.email == email for user in all_users)

    fetched = asyncio.run(services.get_user_by_id(result.id))
    assert fetched is not None
    assert fetched.email == email

    profile = asyncio.run(services.get_profile(TokenData(email=email, id=result.id)))
    assert profile is not None
    assert profile.email == email


def test_auth_db_direct_user_crud():
    email = f"dbuser_{uuid.uuid4().hex[:8]}@example.com"
    created = asyncio.run(create_user_top("dbuser", email, "pass123"))
    assert created.email == email
    assert created.username == "dbuser"

    fetched = asyncio.run(create_user_top("dbuser2", f"{uuid.uuid4().hex[:8]}@example.com", "pass123"))
    assert fetched.email is not None

    by_email = asyncio.run(create_user_db("dbuser3", f"{uuid.uuid4().hex[:8]}@example.com", "pass123"))
    assert by_email.email is not None
    assert asyncio.run(get_user_by_email_db(by_email.email)).email == by_email.email
    assert asyncio.run(get_user_by_id_db(by_email.id)).id == by_email.id

    all_users = asyncio.run(get_all_users_db())
    assert isinstance(all_users, list)

    updated = asyncio.run(update_user_password_db(by_email.id, hashing.get_password_hash("newpassword")))
    assert updated is not None
    assert updated.password != by_email.password

    # Cover top-level auth_db helper functions as well
    top_user = asyncio.run(create_user_top("topuser", f"{uuid.uuid4().hex[:8]}@example.com", "pass123"))
    assert top_user is not None
    assert asyncio.run(create_user_top("topuser2", f"{uuid.uuid4().hex[:8]}@example.com", "pass123")) is not None
    assert asyncio.run(get_user_by_email_db(top_user.email)).email == top_user.email
    assert asyncio.run(get_user_by_id_db(top_user.id)).id == top_user.id
    assert isinstance(asyncio.run(get_all_users_db()), list)
