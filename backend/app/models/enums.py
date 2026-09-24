from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    FACULTY = "FACULTY"
    STUDENT = "STUDENT"


class AttendanceSessionStatus(str, Enum):
    OPEN = "OPEN"
    SUBMITTED = "SUBMITTED"
    LOCKED = "LOCKED"


class AttendanceRecordStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


class CorrectionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
