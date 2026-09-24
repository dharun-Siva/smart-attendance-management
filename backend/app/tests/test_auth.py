from datetime import timedelta

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, require_admin, require_faculty, require_student
from app.core.config import get_settings
from app.core.security import create_access_token, decode_access_token
from app.models.enums import UserRole
PASSWORD = "CorrectPassword123!"


def login(client, identifier: str, password: str = PASSWORD):
    return client.post(
        "/api/v1/auth/login",
        json={"username_or_email": identifier, "password": password},
    )


def test_successful_login_by_username(client, users):
    response = login(client, "admin")

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["user"] == {"id": users[UserRole.ADMIN].id, "username": "admin", "role": "ADMIN"}
    assert "password_hash" not in body
    assert body["access_token"]


def test_successful_login_by_email(client, users):
    response = login(client, "faculty@example.com")

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "FACULTY"


def test_invalid_password_returns_401(client, users):
    response = login(client, "admin", "WrongPassword123!")

    assert response.status_code == 401


def test_invalid_username_returns_401(client, users):
    response = login(client, "missing-user")

    assert response.status_code == 401


def test_inactive_user_returns_401(client, users):
    response = login(client, "inactive")

    assert response.status_code == 401


def test_valid_jwt_and_me_endpoint(client, users):
    token = login(client, "student").json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": users[UserRole.STUDENT].id,
        "username": "student",
        "role": "STUDENT",
    }


def test_missing_or_invalid_jwt_returns_401(client, users):
    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    ).status_code == 401


def test_expired_jwt_returns_401(client, users):
    token = create_access_token(users[UserRole.ADMIN].id, UserRole.ADMIN, timedelta(seconds=-1))

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_jwt_payload_contains_user_identity_and_role(users):
    token = create_access_token(users[UserRole.ADMIN].id, UserRole.ADMIN)
    payload = decode_access_token(token)

    assert payload["sub"] == str(users[UserRole.ADMIN].id)
    assert payload["role"] == "ADMIN"


def test_role_dependencies_allow_matching_role(users):
    assert require_admin(users[UserRole.ADMIN]) is users[UserRole.ADMIN]
    assert require_faculty(users[UserRole.FACULTY]) is users[UserRole.FACULTY]
    assert require_student(users[UserRole.STUDENT]) is users[UserRole.STUDENT]


def test_role_dependencies_reject_other_roles(users):
    with pytest.raises(HTTPException) as admin_error:
        require_admin(users[UserRole.FACULTY])
    with pytest.raises(HTTPException) as faculty_error:
        require_faculty(users[UserRole.STUDENT])
    with pytest.raises(HTTPException) as student_error:
        require_student(users[UserRole.ADMIN])

    assert admin_error.value.status_code == 403
    assert faculty_error.value.status_code == 403
    assert student_error.value.status_code == 403


def test_invalid_signature_is_rejected(db_session: Session, users):
    settings = get_settings()
    token = jwt.encode({"sub": str(users[UserRole.ADMIN].id), "role": "ADMIN"}, "wrong-key", algorithm=settings.jwt_algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    with pytest.raises(HTTPException) as error:
        get_current_user(credentials, db_session)

    assert error.value.status_code == 401
