from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AttendanceRecordStatus, CorrectionStatus


class CorrectionCreate(BaseModel):
    new_status: AttendanceRecordStatus
    reason: str = Field(min_length=1, max_length=500)


class CorrectionReview(BaseModel):
    review_comment: str | None = Field(default=None, max_length=500)


class CorrectionResponse(BaseModel):
    id: int
    attendance_record_id: int
    requested_by_id: int
    old_status: AttendanceRecordStatus
    new_status: AttendanceRecordStatus
    reason: str
    status: CorrectionStatus
    reviewed_by_id: int | None
    review_comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
