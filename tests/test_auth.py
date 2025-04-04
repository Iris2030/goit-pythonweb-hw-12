
import pytest
from sqlalchemy import select

from conf.config import settings
from models.models import User
from tests.conftest import TestingSessionLocal
from jose import jwt
from unittest.mock import Mock
from datetime import datetime, timedelta, UTC
from services.auth import create_email_token
user_data = {"username": "iris",
            "email": "iris@gmail.com",
            "password": "12345678",
            "role":"ADMIN"}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("services.email.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("services.email.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "User with such an email already exists"

def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email address not confirmed"

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("username"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"

def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           data={"username": "username", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Incorrect login or password"

def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data



@pytest.mark.asyncio
async def test_create_email_token(client):
    """
    Tests the creation of an email verification token.
    """
    email_data = {"email": "iris@gmail.com"}

    email_token = create_email_token({"sub": email_data["email"]})

    response = client.post("api/auth/confirm_email", json={"token": email_token})
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email token is valid"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client):
    """
    Tests the refresh endpoint with an invalid refresh token.
    """
    invalid_refresh_token = "invalid_refresh_token_string"

    response = client.post(
        "api/auth/refresh",
        json={"refresh_token": invalid_refresh_token},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid or expired token"

@pytest.mark.asyncio
async def test_refresh_token_expired(client):
    """
    Tests the refresh endpoint with an expired refresh token.
    """
    expired_token_data = {
        "sub": user_data["username"],
        "exp": datetime.now(UTC) - timedelta(seconds=1),
        "token_type": "refresh",
    }
    expired_token = jwt.encode(
        expired_token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    response = client.post(
        "api/auth/refresh",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid or expired refresh token"
