from datetime import date

from pydantic import BaseModel, Field


class ReportFilters(BaseModel):
    department_id: int | None = Field(default=None, gt=0)
    class_id: int | None = Field(default=None, gt=0)
    section_id: int | None = Field(default=None, gt=0)
    subject_id: int | None = Field(default=None, gt=0)
    student_id: int | None = Field(default=None, gt=0)
    start_date: date | None = None
    end_date: date | None = None
    threshold: float = Field(default=75.0, ge=0, le=100)


class AttendanceReportRow(BaseModel):
    student_id: int
    student_number: str
    student_name: str
    department_id: int
    class_id: int
    section_id: int
    subject_id: int | None
    attended_sessions: int
    qualifying_sessions: int
    attendance_percentage: float


class LowAttendanceRow(AttendanceReportRow):
    pass
