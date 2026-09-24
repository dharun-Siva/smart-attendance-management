from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def not_found(entity: str, entity_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{entity} with id {entity_id} was not found",
    )


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def commit_or_conflict(db: Session, detail: str = "Resource already exists") -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict(detail) from None


def flush_or_conflict(db: Session, detail: str = "Resource already exists") -> None:
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise conflict(detail) from None


def add_audit(
    db: Session,
    admin: User,
    action: str,
    entity_type: str,
    entity_id: int,
    description: str,
) -> None:
    db.add(
        AuditLog(
            user_id=admin.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
        )
    )


def duplicate_check(value: object, field: str) -> None:
    if value is not None:
        raise conflict(f"{field} already exists")
