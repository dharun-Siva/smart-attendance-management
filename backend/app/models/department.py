from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Department(TimestampMixin, Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    classes: Mapped[list[Class]] = relationship(back_populates="department")
    subjects: Mapped[list[Subject]] = relationship(back_populates="department")
    faculty_profiles: Mapped[list[FacultyProfile]] = relationship(back_populates="department")
    student_profiles: Mapped[list[StudentProfile]] = relationship(back_populates="department")
