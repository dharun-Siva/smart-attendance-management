from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.enums import AttendanceRecordStatus, AttendanceSessionStatus


class AttendanceSession(TimestampMixin, Base):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        UniqueConstraint(
            "faculty_assignment_id",
            "attendance_date",
            name="uq_sessions_assignment_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("faculty_assignments.id"),
        nullable=False,
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[AttendanceSessionStatus] = mapped_column(
        SAEnum(AttendanceSessionStatus, name="attendance_session_status"),
        default=AttendanceSessionStatus.OPEN,
        nullable=False,
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    faculty_assignment: Mapped[FacultyAssignment] = relationship(
        back_populates="attendance_sessions",
    )
    creator: Mapped[User] = relationship(back_populates="created_sessions")
    records: Mapped[list[AttendanceRecord]] = relationship(
        back_populates="attendance_session",
        cascade="all, delete-orphan",
    )


class AttendanceRecord(TimestampMixin, Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "attendance_session_id",
            "student_id",
            name="uq_records_session_student",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    attendance_session_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sessions.id"),
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=False)
    status: Mapped[AttendanceRecordStatus] = mapped_column(
        SAEnum(AttendanceRecordStatus, name="attendance_record_status"),
        nullable=False,
    )
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)

    attendance_session: Mapped[AttendanceSession] = relationship(back_populates="records")
    student: Mapped[StudentProfile] = relationship(back_populates="attendance_records")
    correction_requests: Mapped[list[AttendanceCorrectionRequest]] = relationship(
        back_populates="attendance_record",
        cascade="all, delete-orphan",
    )
