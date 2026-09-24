from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class StudentEnrollment(TimestampMixin, Base):
    __tablename__ = "student_enrollments"
    __table_args__ = (UniqueConstraint("student_id", "section_id", name="uq_enrollments_student_section"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"), nullable=False)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    student: Mapped[StudentProfile] = relationship(back_populates="enrollments")
    section: Mapped[Section] = relationship(back_populates="enrollments")
