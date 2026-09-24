from __future__ import annotations

from sqlalchemy import Boolean, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.enums import UserRole


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    faculty_profile: Mapped[FacultyProfile | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_profile: Mapped[StudentProfile | None] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    created_sessions: Mapped[list[AttendanceSession]] = relationship(
        back_populates="creator",
    )
    requested_corrections: Mapped[list[AttendanceCorrectionRequest]] = relationship(
        back_populates="requester",
        foreign_keys="AttendanceCorrectionRequest.requested_by_id",
    )
    reviewed_corrections: Mapped[list[AttendanceCorrectionRequest]] = relationship(
        back_populates="reviewer",
        foreign_keys="AttendanceCorrectionRequest.reviewed_by_id",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="user")
