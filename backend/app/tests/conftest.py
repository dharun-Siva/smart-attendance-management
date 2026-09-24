from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.enums import UserRole
from app.models.user import User

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=_test_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(_test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(_test_engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def users(db_session: Session) -> dict[UserRole, User]:
    created_users = {}
    for index, role in enumerate(UserRole, start=1):
        user = User(
            username=role.value.lower(),
            email=f"{role.value.lower()}@example.com",
            password_hash=hash_password("CorrectPassword123!"),
            role=role,
            is_active=True,
        )
        db_session.add(user)
        created_users[role] = user

    inactive_user = User(
        username="inactive",
        email="inactive@example.com",
        password_hash=hash_password("CorrectPassword123!"),
        role=UserRole.STUDENT,
        is_active=False,
    )
    db_session.add(inactive_user)
    db_session.commit()
    return created_users
