from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.assignment import FacultyAssignment
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.class_section import Section
from app.models.enrollment import StudentEnrollment
from app.models.enums import AttendanceRecordStatus, AttendanceSessionStatus, UserRole
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from app.models.subject import Subject
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
    StudentSubjectAttendanceResponse,
)
from app.services.admin_service import add_audit, conflict, not_found


def not_allowed(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def bad_request(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def get_assignment(db: Session, assignment_id: int) -> FacultyAssignment:
    assignment = db.scalar(
        select(FacultyAssignment)
        .options(selectinload(FacultyAssignment.faculty).selectinload(FacultyProfile.user))
        .where(FacultyAssignment.id == assignment_id)
    )
    if assignment is None:
        raise not_found("Faculty assignment", assignment_id)
    return assignment


def get_accessible_assignment(
    db: Session,
    assignment_id: int,
    user: User,
    require_active: bool = True,
) -> FacultyAssignment:
    assignment = get_assignment(db, assignment_id)
    if user.role == UserRole.FACULTY:
        if user.faculty_profile is None or assignment.faculty_id != user.faculty_profile.id:
            raise not_allowed("You do not own this faculty assignment")
    elif user.role != UserRole.ADMIN:
        raise not_allowed("Only administrators and faculty can access attendance")
    if require_active and not assignment.is_active:
        raise bad_request("Faculty assignment is inactive")
    return assignment


def get_accessible_session(
    db: Session,
    session_id: int,
    user: User,
) -> AttendanceSession:
    attendance_session = db.scalar(
        select(AttendanceSession)
        .options(selectinload(AttendanceSession.faculty_assignment))
        .where(AttendanceSession.id == session_id)
    )
    if attendance_session is None:
        raise not_found("Attendance session", session_id)
    assignment = attendance_session.faculty_assignment
    if user.role == UserRole.FACULTY:
        if user.faculty_profile is None or assignment.faculty_id != user.faculty_profile.id:
            raise not_allowed("You do not own this attendance session")
    elif user.role != UserRole.ADMIN:
        raise not_allowed("Students cannot access faculty attendance sessions")
    return attendance_session


def ensure_active_session_context(db: Session, assignment: FacultyAssignment) -> None:
    if not assignment.is_active:
        raise bad_request("Faculty assignment is inactive")
    section = db.get(Section, assignment.section_id)
    subject = db.get(Subject, assignment.subject_id)
    if section is None:
        raise not_found("Section", assignment.section_id)
    if subject is None:
        raise not_found("Subject", assignment.subject_id)
    if not section.is_active:
        raise bad_request("Section is inactive")
    if not subject.is_active:
        raise bad_request("Subject is inactive")


def create_session(
    db: Session,
    user: User,
    payload: AttendanceSessionCreate,
) -> AttendanceSession:
    assignment = get_accessible_assignment(db, payload.faculty_assignment_id, user)
    ensure_active_session_context(db, assignment)
    duplicate = db.scalar(
        select(AttendanceSession).where(
            AttendanceSession.faculty_assignment_id == payload.faculty_assignment_id,
            AttendanceSession.attendance_date == payload.attendance_date,
        )
    )
    if duplicate:
        raise conflict("Attendance session already exists for this assignment and date")

    attendance_session = AttendanceSession(
        faculty_assignment_id=payload.faculty_assignment_id,
        attendance_date=payload.attendance_date,
        topic=payload.topic,
        created_by=user.id,
        status=AttendanceSessionStatus.OPEN,
    )
    db.add(attendance_session)
    try:
        db.flush()
        add_audit(
            db,
            user,
            "CREATE",
            "attendance_session",
            attendance_session.id,
            f"Created attendance session for {payload.attendance_date}",
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict("Attendance session already exists for this assignment and date") from None
    return attendance_session


def list_sessions(db: Session, user: User) -> list[AttendanceSession]:
    query = select(AttendanceSession).order_by(AttendanceSession.attendance_date.desc(), AttendanceSession.id.desc())
    if user.role == UserRole.FACULTY:
        if user.faculty_profile is None:
            raise not_allowed("Faculty profile is required")
        query = query.join(AttendanceSession.faculty_assignment).where(
            FacultyAssignment.faculty_id == user.faculty_profile.id,
            FacultyAssignment.is_active.is_(True),
        )
    elif user.role != UserRole.ADMIN:
        raise not_allowed("Students cannot access attendance sessions")
    return list(db.scalars(query).all())


def list_assignments(db: Session, user: User) -> list[FacultyAssignment]:
    query = select(FacultyAssignment).options(
        selectinload(FacultyAssignment.subject).selectinload(Subject.department),
        selectinload(FacultyAssignment.section).selectinload(Section.class_),
    ).order_by(FacultyAssignment.id)
    if user.role == UserRole.FACULTY:
        if user.faculty_profile is None:
            raise not_allowed("Faculty profile is required")
        query = query.where(
            FacultyAssignment.faculty_id == user.faculty_profile.id,
            FacultyAssignment.is_active.is_(True),
        )
    elif user.role == UserRole.ADMIN:
        pass
    else:
        raise not_allowed("Students cannot access faculty assignments")
    return list(db.scalars(query).all())


def assignment_response(assignment: FacultyAssignment) -> AttendanceAssignmentResponse:
    return AttendanceAssignmentResponse(
        id=assignment.id,
        faculty_id=assignment.faculty_id,
        subject_id=assignment.subject_id,
        section_id=assignment.section_id,
        is_active=assignment.is_active,
        subject_name=assignment.subject.name,
        section_name=assignment.section.name,
        class_name=assignment.section.class_.name,
        department_name=assignment.subject.department.name,
    )


def session_response(attendance_session: AttendanceSession) -> AttendanceSessionResponse:
    return AttendanceSessionResponse.model_validate(attendance_session)


def record_response(record: AttendanceRecord) -> AttendanceRecordResponse:
    return AttendanceRecordResponse(
        id=record.id,
        attendance_session_id=record.attendance_session_id,
        student_id=record.student_id,
        student_number=record.student.student_number,
        student_name=f"{record.student.first_name} {record.student.last_name}",
        status=record.status,
        remarks=record.remarks,
    )


def get_records(db: Session, attendance_session: AttendanceSession) -> list[AttendanceRecordResponse]:
    records = db.scalars(
        select(AttendanceRecord)
        .join(AttendanceRecord.student)
        .join(
            StudentEnrollment,
            (StudentEnrollment.student_id == AttendanceRecord.student_id)
            & (StudentEnrollment.is_active.is_(True)),
        )
        .where(
            AttendanceRecord.attendance_session_id == attendance_session.id,
            StudentEnrollment.section_id == attendance_session.faculty_assignment.section_id,
        )
        .options(selectinload(AttendanceRecord.student))
        .order_by(AttendanceRecord.student_id)
    ).all()
    records_by_student = {record.student_id: record for record in records}
    enrolled_students = db.scalars(
        select(StudentProfile)
        .join(
            StudentEnrollment,
            (StudentEnrollment.student_id == StudentProfile.id)
            & (StudentEnrollment.is_active.is_(True)),
        )
        .where(StudentEnrollment.section_id == attendance_session.faculty_assignment.section_id)
        .order_by(StudentProfile.id)
    ).all()
    response = []
    for student in enrolled_students:
        record = records_by_student.get(student.id)
        if record is not None:
            response.append(record_response(record))
        else:
            response.append(
                AttendanceRecordResponse(
                    id=-student.id,
                    attendance_session_id=attendance_session.id,
                    student_id=student.id,
                    student_number=student.student_number,
                    student_name=f"{student.first_name} {student.last_name}",
                    status=AttendanceRecordStatus.ABSENT,
                    remarks=None,
                )
            )
    return response


def update_records(
    db: Session,
    user: User,
    attendance_session: AttendanceSession,
    payload: AttendanceRecordsUpdate,
) -> list[AttendanceRecordResponse]:
    if attendance_session.status != AttendanceSessionStatus.OPEN:
        raise bad_request("Attendance session can no longer be edited")
    ensure_active_session_context(db, attendance_session.faculty_assignment)

    student_ids = [record.student_id for record in payload.records]
    if len(student_ids) != len(set(student_ids)):
        raise conflict("Duplicate student records are not allowed")
    enrolled_students = set(
        db.scalars(
            select(StudentEnrollment.student_id).where(
                StudentEnrollment.section_id == attendance_session.faculty_assignment.section_id,
                StudentEnrollment.student_id.in_(student_ids),
                StudentEnrollment.is_active.is_(True),
            )
        ).all()
    )
    missing_students = sorted(set(student_ids) - enrolled_students)
    if missing_students:
        raise bad_request(f"Students are not enrolled in this section: {missing_students}")

    existing_records = {
        record.student_id: record
        for record in db.scalars(
            select(AttendanceRecord).where(
                AttendanceRecord.attendance_session_id == attendance_session.id,
                AttendanceRecord.student_id.in_(student_ids),
            )
        ).all()
    }
    changed_records: list[AttendanceRecord] = []
    try:
        for item in payload.records:
            record = existing_records.get(item.student_id)
            if record is None:
                record = AttendanceRecord(
                    attendance_session_id=attendance_session.id,
                    student_id=item.student_id,
                    status=item.status,
                    remarks=item.remarks,
                )
                db.add(record)
            else:
                record.status = item.status
                record.remarks = item.remarks
            changed_records.append(record)
        db.flush()
        for record in changed_records:
            add_audit(
                db,
                user,
                "UPDATE",
                "attendance_record",
                record.id,
                f"Changed attendance for student {record.student_id}",
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise conflict("Attendance record could not be saved") from None
    return get_records(db, attendance_session)


def submit_session(db: Session, user: User, attendance_session: AttendanceSession) -> AttendanceSession:
    if attendance_session.status != AttendanceSessionStatus.OPEN:
        raise bad_request("Only open attendance sessions can be submitted")
    ensure_active_session_context(db, attendance_session.faculty_assignment)
    enrolled_ids = set(
        db.scalars(
            select(StudentEnrollment.student_id).where(
                StudentEnrollment.section_id == attendance_session.faculty_assignment.section_id,
                StudentEnrollment.is_active.is_(True),
            )
        ).all()
    )
    recorded_ids = set(
        db.scalars(
            select(AttendanceRecord.student_id).where(
                AttendanceRecord.attendance_session_id == attendance_session.id,
            )
        ).all()
    )
    missing_ids = sorted(enrolled_ids - recorded_ids)
    if missing_ids:
        raise bad_request(f"Attendance is missing for students: {missing_ids}")
    attendance_session.status = AttendanceSessionStatus.SUBMITTED
    attendance_session.submitted_at = datetime.now(timezone.utc)
    add_audit(db, user, "SUBMIT", "attendance_session", attendance_session.id, "Submitted attendance session")
    db.commit()
    return attendance_session


def lock_session(db: Session, user: User, attendance_session: AttendanceSession) -> AttendanceSession:
    if user.role != UserRole.ADMIN:
        raise not_allowed("Only administrators can lock attendance sessions")
    if attendance_session.status != AttendanceSessionStatus.SUBMITTED:
        raise bad_request("Only submitted attendance sessions can be locked")
    attendance_session.status = AttendanceSessionStatus.LOCKED
    add_audit(db, user, "LOCK", "attendance_session", attendance_session.id, "Locked attendance session")
    db.commit()
    return attendance_session


def student_history(db: Session, student: StudentProfile) -> list[AttendanceHistoryResponse]:
    records = db.scalars(
        select(AttendanceRecord)
        .join(AttendanceRecord.attendance_session)
        .join(AttendanceSession.faculty_assignment)
        .join(FacultyAssignment.subject)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceSession.status != AttendanceSessionStatus.OPEN,
        )
        .options(
            selectinload(AttendanceRecord.attendance_session),
            selectinload(AttendanceRecord.attendance_session, AttendanceSession.faculty_assignment).selectinload(
                FacultyAssignment.subject
            ),
        )
        .order_by(AttendanceSession.attendance_date.desc())
    ).all()
    return [
        AttendanceHistoryResponse(
            attendance_session_id=record.attendance_session_id,
            attendance_date=record.attendance_session.attendance_date,
            subject_id=record.attendance_session.faculty_assignment.subject_id,
            subject_name=record.attendance_session.faculty_assignment.subject.name,
            topic=record.attendance_session.topic,
            status=record.status,
            remarks=record.remarks,
        )
        for record in records
    ]


def calculate_percentage(records: list[AttendanceRecord]) -> AttendancePercentageResponse:
    qualifying = [record for record in records if record.status != AttendanceRecordStatus.EXCUSED]
    attended = sum(record.status in {AttendanceRecordStatus.PRESENT, AttendanceRecordStatus.LATE} for record in qualifying)
    qualifying_count = len(qualifying)
    percentage = round((attended / qualifying_count) * 100, 2) if qualifying_count else 0.0
    return AttendancePercentageResponse(
        attended_sessions=attended,
        qualifying_sessions=qualifying_count,
        attendance_percentage=percentage,
    )


def student_attendance_summary(db: Session, student: StudentProfile) -> StudentAttendanceSummaryResponse:
    threshold = 75.0
    profile = db.scalar(
        select(StudentProfile)
        .options(
            selectinload(StudentProfile.user),
            selectinload(StudentProfile.department),
            selectinload(StudentProfile.enrollments).selectinload(StudentEnrollment.section).selectinload(Section.class_),
        )
        .where(StudentProfile.id == student.id)
    )
    records = db.execute(
        select(AttendanceRecord, Subject)
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .join(FacultyAssignment, AttendanceSession.faculty_assignment_id == FacultyAssignment.id)
        .join(Subject, FacultyAssignment.subject_id == Subject.id)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceSession.status != AttendanceSessionStatus.OPEN,
        )
    ).all()

    grouped: dict[int, tuple[Subject, list[AttendanceRecord]]] = {}
    for record, subject in records:
        grouped.setdefault(subject.id, (subject, []))[1].append(record)

    def counts(items: list[AttendanceRecord]) -> tuple[int, int, int, int, int, float]:
        present = sum(item.status == AttendanceRecordStatus.PRESENT for item in items)
        absent = sum(item.status == AttendanceRecordStatus.ABSENT for item in items)
        late = sum(item.status == AttendanceRecordStatus.LATE for item in items)
        excused = sum(item.status == AttendanceRecordStatus.EXCUSED for item in items)
        qualifying = present + absent + late
        percentage = round(((present + late) / qualifying) * 100, 2) if qualifying else 0.0
        return len(items), present, absent, late, excused, percentage

    _total, present, absent, late, excused, percentage = counts([record for record, _subject in records])
    section = next((enrollment.section for enrollment in profile.enrollments if enrollment.is_active), None)
    subjects = []
    for subject, items in grouped.values():
        subject_total, subject_present, subject_absent, subject_late, subject_excused, subject_percentage = counts(items)
        subjects.append(
            StudentSubjectAttendanceResponse(
                subject_name=subject.name,
                subject_code=subject.code,
                total_sessions=subject_total,
                present_sessions=subject_present,
                absent_sessions=subject_absent,
                late_sessions=subject_late,
                excused_sessions=subject_excused,
                attendance_percentage=subject_percentage,
                is_low_attendance=subject_percentage < threshold,
            )
        )
    return StudentAttendanceSummaryResponse(
        student_name=f"{profile.first_name} {profile.last_name}",
        student_number=profile.student_number,
        email=profile.user.email,
        department_name=profile.department.name,
        class_name=section.class_.name if section else None,
        section_name=section.name if section else None,
        attendance_percentage=percentage,
        present_sessions=present,
        absent_sessions=absent,
        late_sessions=late,
        excused_sessions=excused,
        low_attendance_threshold=threshold,
        subjects=sorted(subjects, key=lambda item: item.subject_name),
    )


def student_percentage(db: Session, student: StudentProfile) -> AttendancePercentageResponse:
    records = db.scalars(
        select(AttendanceRecord)
        .join(AttendanceRecord.attendance_session)
        .where(
            AttendanceRecord.student_id == student.id,
            AttendanceSession.status != AttendanceSessionStatus.OPEN,
        )
    ).all()
    return calculate_percentage(list(records))


def faculty_student_percentage(
    db: Session,
    user: User,
    student_id: int,
) -> AttendancePercentageResponse:
    student = db.get(StudentProfile, student_id)
    if student is None:
        raise not_found("Student", student_id)
    if user.role == UserRole.FACULTY:
        if user.faculty_profile is None:
            raise not_allowed("Faculty profile is required")
        accessible_sections = set(
            db.scalars(
                select(FacultyAssignment.section_id).where(
                    FacultyAssignment.faculty_id == user.faculty_profile.id,
                    FacultyAssignment.is_active.is_(True),
                )
            ).all()
        )
        enrolled = db.scalar(
            select(StudentEnrollment.id).where(
                StudentEnrollment.student_id == student_id,
                StudentEnrollment.section_id.in_(accessible_sections or {-1}),
                StudentEnrollment.is_active.is_(True),
            )
        )
        if enrolled is None:
            raise not_allowed("Student is not in one of your assigned sections")
        records = db.scalars(
            select(AttendanceRecord)
            .join(AttendanceRecord.attendance_session)
            .join(AttendanceSession.faculty_assignment)
            .where(
                AttendanceRecord.student_id == student_id,
                FacultyAssignment.faculty_id == user.faculty_profile.id,
                FacultyAssignment.is_active.is_(True),
                AttendanceSession.status != AttendanceSessionStatus.OPEN,
            )
        ).all()
    elif user.role == UserRole.ADMIN:
        records = db.scalars(
            select(AttendanceRecord)
            .join(AttendanceRecord.attendance_session)
            .where(
                AttendanceRecord.student_id == student_id,
                AttendanceSession.status != AttendanceSessionStatus.OPEN,
            )
        ).all()
    else:
        raise not_allowed("Students can only view their own attendance")
    return calculate_percentage(list(records))
