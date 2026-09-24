from __future__ import annotations

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.enums import AttendanceRecordStatus, CorrectionStatus


class AttendanceCorrectionRequest(TimestampMixin, Base):
    __tablename__ = "attendance_correction_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    attendance_record_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_records.id"),
        nullable=False,
    )
    requested_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    old_status: Mapped[AttendanceRecordStatus] = mapped_column(
        SAEnum(AttendanceRecordStatus, name="attendance_record_status"),
        nullable=False,
    )
    new_status: Mapped[AttendanceRecordStatus] = mapped_column(
        SAEnum(AttendanceRecordStatus, name="attendance_record_status"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[CorrectionStatus] = mapped_column(
        SAEnum(CorrectionStatus, name="correction_status"),
        default=CorrectionStatus.PENDING,
        nullable=False,
    )
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    review_comment: Mapped[str | None] = mapped_column(String(500), nullable=True)

    attendance_record: Mapped[AttendanceRecord] = relationship(
        back_populates="correction_requests",
    )
    requester: Mapped[User] = relationship(
        back_populates="requested_corrections",
        foreign_keys=[requested_by_id],
    )
    reviewer: Mapped[User | None] = relationship(
        back_populates="reviewed_corrections",
        foreign_keys=[reviewed_by_id],
    )
