from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import AdminUser, CurrentUser, StudentUser
from app.core.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.attendance import (
    AttendanceAssignmentResponse,
    AttendanceHistoryResponse,
    AttendancePercentageResponse,
    AttendanceRecordResponse,
    AttendanceRecordsUpdate,
    AttendanceSessionCreate,
    AttendanceSessionResponse,
    StudentAttendanceSummaryResponse,
)
from app.services.attendance_service import (
    assignment_response,
    create_session,
    faculty_student_percentage,
    get_accessible_session,
    get_records,
    list_assignments,
    list_sessions,
    lock_session,
    session_response,
    student_history,
    student_attendance_summary,
    student_percentage,
    submit_session,
    update_records,
)

router = APIRouter(prefix="/attendance")


def require_attendance_manager(user: CurrentUser) -> User:
    if user.role not in {UserRole.ADMIN, UserRole.FACULTY}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and faculty can manage attendance",
        )
    return user


AttendanceManagerUser = Annotated[User, Depends(require_attendance_manager)]


@router.get("/assignments", response_model=list[AttendanceAssignmentResponse])
def get_attendance_assignments(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return [assignment_response(item) for item in list_assignments(db, current_user)]


@router.post("/sessions", response_model=AttendanceSessionResponse, status_code=status.HTTP_201_CREATED)
def create_attendance_session(
    payload: AttendanceSessionCreate,
    current_user: AttendanceManagerUser,
    db: Session = Depends(get_db),
):
    return session_response(create_session(db, current_user, payload))


@router.get("/sessions", response_model=list[AttendanceSessionResponse])
def get_attendance_sessions(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return [session_response(item) for item in list_sessions(db, current_user)]


@router.get("/sessions/{session_id}", response_model=AttendanceSessionResponse)
def get_attendance_session(
    session_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return session_response(get_accessible_session(db, session_id, current_user))


@router.get("/sessions/{session_id}/records", response_model=list[AttendanceRecordResponse])
def get_attendance_records(
    session_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    attendance_session = get_accessible_session(db, session_id, current_user)
    return get_records(db, attendance_session)


@router.put("/sessions/{session_id}/records", response_model=list[AttendanceRecordResponse])
def put_attendance_records(
    session_id: int,
    payload: AttendanceRecordsUpdate,
    current_user: AttendanceManagerUser,
    db: Session = Depends(get_db),
):
    attendance_session = get_accessible_session(db, session_id, current_user)
    return update_records(db, current_user, attendance_session, payload)


@router.post("/sessions/{session_id}/submit", response_model=AttendanceSessionResponse)
def submit_attendance_session(
    session_id: int,
    current_user: AttendanceManagerUser,
    db: Session = Depends(get_db),
):
    attendance_session = get_accessible_session(db, session_id, current_user)
    return session_response(submit_session(db, current_user, attendance_session))


@router.post("/sessions/{session_id}/lock", response_model=AttendanceSessionResponse)
def lock_attendance_session(
    session_id: int,
    admin: AdminUser,
    db: Session = Depends(get_db),
):
    attendance_session = get_accessible_session(db, session_id, admin)
    return session_response(lock_session(db, admin, attendance_session))


@router.get("/students/me/history", response_model=list[AttendanceHistoryResponse])
def get_my_attendance_history(
    student: StudentUser,
    db: Session = Depends(get_db),
):
    if student.student_profile is None:
        raise HTTPException(status_code=403, detail="Student profile is required")
    return student_history(db, student.student_profile)


@router.get("/students/me/summary", response_model=StudentAttendanceSummaryResponse)
def get_my_attendance_summary(
    student: StudentUser,
    db: Session = Depends(get_db),
):
    if student.student_profile is None:
        raise HTTPException(status_code=403, detail="Student profile is required")
    return student_attendance_summary(db, student.student_profile)


@router.get("/students/me/percentage", response_model=AttendancePercentageResponse)
def get_my_attendance_percentage(
    student: StudentUser,
    db: Session = Depends(get_db),
):
    if student.student_profile is None:
        raise HTTPException(status_code=403, detail="Student profile is required")
    return student_percentage(db, student.student_profile)


@router.get("/students/{student_id}/percentage", response_model=AttendancePercentageResponse)
def get_student_attendance_percentage(
    student_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return faculty_student_percentage(db, current_user, student_id)
