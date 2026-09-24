from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import InvalidTokenError, decode_access_token
from app.models.enums import UserRole
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise authentication_error()

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")
        user_id = int(subject) if subject is not None else None
    except (InvalidTokenError, TypeError, ValueError):
        raise authentication_error() from None

    if user_id is None:
        raise authentication_error()

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise authentication_error()

    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user


def require_faculty(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.FACULTY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Faculty role required")
    return current_user


def require_student(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student role required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
FacultyUser = Annotated[User, Depends(require_faculty)]
StudentUser = Annotated[User, Depends(require_student)]
