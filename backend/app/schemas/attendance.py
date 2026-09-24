from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AttendanceRecordStatus, AttendanceSessionStatus


class AttendanceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AttendanceSessionCreate(BaseModel):
    faculty_assignment_id: int = Field(gt=0)
    attendance_date: date
    topic: str | None = Field(default=None, max_length=255)


class AttendanceSessionResponse(AttendanceBase):
    id: int
    faculty_assignment_id: int
    attendance_date: date
    topic: str | None
    status: AttendanceSessionStatus
    created_by: int
    submitted_at: datetime | None


class AttendanceRecordInput(BaseModel):
    student_id: int = Field(gt=0)
    status: AttendanceRecordStatus
    remarks: str | None = Field(default=None, max_length=255)


class AttendanceRecordsUpdate(BaseModel):
    records: list[AttendanceRecordInput] = Field(min_length=1)


class AttendanceRecordResponse(AttendanceBase):
    id: int
    attendance_session_id: int
    student_id: int
    student_number: str
    student_name: str
    status: AttendanceRecordStatus
    remarks: str | None


class AttendanceHistoryResponse(AttendanceBase):
    attendance_session_id: int
    attendance_date: date
    subject_id: int
    subject_name: str
    topic: str | None
    status: AttendanceRecordStatus
    remarks: str | None


class AttendancePercentageResponse(BaseModel):
    attended_sessions: int
    qualifying_sessions: int
    attendance_percentage: float


class StudentSubjectAttendanceResponse(BaseModel):
    subject_name: str
    subject_code: str
    total_sessions: int
    present_sessions: int
    absent_sessions: int
    late_sessions: int
    excused_sessions: int
    attendance_percentage: float
    is_low_attendance: bool


class StudentAttendanceSummaryResponse(BaseModel):
    student_name: str
    student_number: str
    email: str
    department_name: str
    class_name: str | None
    section_name: str | None
    attendance_percentage: float
    present_sessions: int
    absent_sessions: int
    late_sessions: int
    excused_sessions: int
    low_attendance_threshold: float
    subjects: list[StudentSubjectAttendanceResponse]


class AttendanceAssignmentResponse(AttendanceBase):
    id: int
    faculty_id: int
    subject_id: int
    section_id: int
    is_active: bool
    subject_name: str
    section_name: str
    class_name: str
    department_name: str
