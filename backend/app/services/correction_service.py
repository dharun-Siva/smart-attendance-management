from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.correction import AttendanceCorrectionRequest
from app.models.enums import AttendanceSessionStatus, CorrectionStatus, UserRole
from app.models.user import User
from app.schemas.correction import CorrectionCreate, CorrectionResponse, CorrectionReview
from app.services.admin_service import add_audit, conflict, not_found
from app.services.attendance_service import not_allowed


def get_record(db: Session, record_id: int) -> AttendanceRecord:
    record = db.scalar(
        select(AttendanceRecord)
        .options(
            selectinload(AttendanceRecord.attendance_session).selectinload(
                AttendanceSession.faculty_assignment
            )
        )
        .where(AttendanceRecord.id == record_id)
    )
    if record is None:
        raise not_found("Attendance record", record_id)
    return record


def ensure_faculty_owns_record(record: AttendanceRecord, faculty: User) -> None:
    if faculty.role != UserRole.FACULTY:
        raise not_allowed("Only faculty can request attendance corrections")
    if faculty.faculty_profile is None or record.attendance_session.faculty_assignment.faculty_id != faculty.faculty_profile.id:
        raise not_allowed("You do not own this attendance record")


def request_correction(
    db: Session,
    faculty: User,
    record_id: int,
    payload: CorrectionCreate,
) -> AttendanceCorrectionRequest:
    record = get_record(db, record_id)
    ensure_faculty_owns_record(record, faculty)
    if record.attendance_session.status not in {
        AttendanceSessionStatus.SUBMITTED,
        AttendanceSessionStatus.LOCKED,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrections are available only for submitted or locked sessions",
        )
    if payload.new_status == record.status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New attendance status must differ from the current status",
        )
    pending = db.scalar(
        select(AttendanceCorrectionRequest).where(
            AttendanceCorrectionRequest.attendance_record_id == record_id,
            AttendanceCorrectionRequest.status == CorrectionStatus.PENDING,
        )
    )
    if pending:
        raise conflict("A pending correction already exists for this attendance record")
    correction = AttendanceCorrectionRequest(
        attendance_record_id=record.id,
        requested_by_id=faculty.id,
        old_status=record.status,
        new_status=payload.new_status,
        reason=payload.reason,
        status=CorrectionStatus.PENDING,
    )
    db.add(correction)
    try:
        db.flush()
        add_audit(
            db,
            faculty,
            "CREATE",
            "attendance_correction",
            correction.id,
            f"Requested correction for attendance record {record.id}",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict("A pending correction already exists for this attendance record") from None
    return correction


def list_corrections(db: Session, user: User) -> list[AttendanceCorrectionRequest]:
    if user.role == UserRole.ADMIN:
        query = select(AttendanceCorrectionRequest).order_by(AttendanceCorrectionRequest.id.desc())
    elif user.role == UserRole.FACULTY:
        query = select(AttendanceCorrectionRequest).where(
            AttendanceCorrectionRequest.requested_by_id == user.id
        ).order_by(AttendanceCorrectionRequest.id.desc())
    else:
        raise not_allowed("Students cannot access correction requests")
    return list(db.scalars(query).all())


def get_correction(db: Session, user: User, correction_id: int) -> AttendanceCorrectionRequest:
    correction = db.get(AttendanceCorrectionRequest, correction_id)
    if correction is None:
        raise not_found("Correction request", correction_id)
    if user.role == UserRole.ADMIN:
        return correction
    if user.role == UserRole.FACULTY and correction.requested_by_id == user.id:
        return correction
    raise not_allowed("You cannot access this correction request")


def review_correction(
    db: Session,
    admin: User,
    correction_id: int,
    payload: CorrectionReview,
    approved: bool,
) -> AttendanceCorrectionRequest:
    correction = db.scalar(
        select(AttendanceCorrectionRequest)
        .options(selectinload(AttendanceCorrectionRequest.attendance_record))
        .where(AttendanceCorrectionRequest.id == correction_id)
    )
    if correction is None:
        raise not_found("Correction request", correction_id)
    if correction.status != CorrectionStatus.PENDING:
        raise conflict("This correction request has already been processed")

    if approved:
        correction.attendance_record.status = correction.new_status
        correction.status = CorrectionStatus.APPROVED
        action = "APPROVE"
        description = f"Approved correction request {correction.id}"
    else:
        correction.status = CorrectionStatus.REJECTED
        action = "REJECT"
        description = f"Rejected correction request {correction.id}"
    correction.reviewed_by_id = admin.id
    correction.review_comment = payload.review_comment
    add_audit(db, admin, action, "attendance_correction", correction.id, description)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Correction review could not be saved") from None
    return correction


def correction_response(correction: AttendanceCorrectionRequest) -> CorrectionResponse:
    return CorrectionResponse.model_validate(correction)
