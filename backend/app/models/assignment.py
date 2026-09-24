from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class FacultyAssignment(TimestampMixin, Base):
    __tablename__ = "faculty_assignments"
    __table_args__ = (
        UniqueConstraint(
            "faculty_id",
            "subject_id",
            "section_id",
            name="uq_assignments_faculty_subject_section",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    faculty_id: Mapped[int] = mapped_column(ForeignKey("faculty_profiles.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    faculty: Mapped[FacultyProfile] = relationship(back_populates="assignments")
    subject: Mapped[Subject] = relationship(back_populates="faculty_assignments")
    section: Mapped[Section] = relationship(back_populates="faculty_assignments")
    attendance_sessions: Mapped[list[AttendanceSession]] = relationship(
        back_populates="faculty_assignment",
        cascade="all, delete-orphan",
    )
