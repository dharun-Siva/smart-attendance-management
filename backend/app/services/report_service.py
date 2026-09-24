from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assignment import FacultyAssignment
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.class_section import Class as ClassModel
from app.models.enrollment import StudentEnrollment
from app.models.enums import AttendanceRecordStatus, AttendanceSessionStatus, UserRole
from app.models.class_section import Section
from app.models.student import StudentProfile
from app.models.subject import Subject
from app.models.user import User
from app.schemas.report import AttendanceReportRow, LowAttendanceRow, ReportFilters
from app.services.attendance_service import not_allowed


def _base_query():
    return (
        select(
            AttendanceRecord,
            StudentProfile,
            FacultyAssignment,
            AttendanceSession,
            Subject,
            Section,
            ClassModel,
        )
        .join(AttendanceSession, AttendanceRecord.attendance_session_id == AttendanceSession.id)
        .join(FacultyAssignment, AttendanceSession.faculty_assignment_id == FacultyAssignment.id)
        .join(StudentProfile, AttendanceRecord.student_id == StudentProfile.id)
        .join(Subject, FacultyAssignment.subject_id == Subject.id)
        .join(Section, FacultyAssignment.section_id == Section.id)
        .join(ClassModel, Section.class_id == ClassModel.id)
        .where(AttendanceSession.status != AttendanceSessionStatus.OPEN)
    )


def _faculty_assignment_ids(db: Session, user: User) -> set[int]:
    if user.faculty_profile is None:
        raise not_allowed("Faculty profile is required")
    return set(
        db.scalars(
            select(FacultyAssignment.id).where(
                FacultyAssignment.faculty_id == user.faculty_profile.id,
                FacultyAssignment.is_active.is_(True),
            )
        ).all()
    )


def _ensure_faculty_scope(
    db: Session,
    user: User,
    section_id: int | None = None,
    subject_id: int | None = None,
    student_id: int | None = None,
) -> set[int] | None:
    if user.role == UserRole.ADMIN:
        return None
    if user.role != UserRole.FACULTY:
        if (
            user.role == UserRole.STUDENT
            and student_id is not None
            and user.student_profile is not None
            and user.student_profile.id == student_id
        ):
            return None
        raise not_allowed("Students cannot access this report")
    assignment_ids = _faculty_assignment_ids(db, user)
    query = select(FacultyAssignment.id).where(FacultyAssignment.id.in_(assignment_ids or {-1}))
    if section_id is not None:
        query = query.where(FacultyAssignment.section_id == section_id)
    if subject_id is not None:
        query = query.where(FacultyAssignment.subject_id == subject_id)
    if student_id is not None:
        query = query.join(
            StudentEnrollment,
            (StudentEnrollment.section_id == FacultyAssignment.section_id)
            & (StudentEnrollment.student_id == student_id)
            & (StudentEnrollment.is_active.is_(True)),
        )
    if db.scalar(query.limit(1)) is None:
        raise not_allowed("You do not have access to this report scope")
    return assignment_ids


def _rows(
    db: Session,
    user: User,
    filters: ReportFilters,
    fixed_student_id: int | None = None,
    fixed_section_id: int | None = None,
    fixed_subject_id: int | None = None,
) -> list[AttendanceReportRow]:
    student_id = fixed_student_id or filters.student_id
    section_id = fixed_section_id or filters.section_id
    subject_id = fixed_subject_id or filters.subject_id
    assignment_ids = _ensure_faculty_scope(db, user, section_id, subject_id, student_id)
    query = _base_query()
    if assignment_ids is not None:
        query = query.where(FacultyAssignment.id.in_(assignment_ids or {-1}))
    if filters.department_id is not None:
        query = query.where(ClassModel.department_id == filters.department_id)
    if filters.class_id is not None:
        query = query.where(ClassModel.id == filters.class_id)
    if section_id is not None:
        query = query.where(FacultyAssignment.section_id == section_id)
    if subject_id is not None:
        query = query.where(FacultyAssignment.subject_id == subject_id)
    if student_id is not None:
        query = query.where(AttendanceRecord.student_id == student_id)
    if filters.start_date is not None:
        query = query.where(AttendanceSession.attendance_date >= filters.start_date)
    if filters.end_date is not None:
        query = query.where(AttendanceSession.attendance_date <= filters.end_date)

    grouped: dict[int, list[tuple[AttendanceRecord, StudentProfile, FacultyAssignment, Subject, Section, ClassModel]]] = defaultdict(list)
    for record, student, assignment, _session, subject, section, class_item in db.execute(query).all():
        grouped[student.id].append((record, student, assignment, subject, section, class_item))

    result = []
    for student_records in grouped.values():
        first_record, student, _assignment, _subject, _section, _class_item = student_records[0]
        qualifying = [item for item in student_records if item[0].status != AttendanceRecordStatus.EXCUSED]
        attended = sum(item[0].status in {AttendanceRecordStatus.PRESENT, AttendanceRecordStatus.LATE} for item in qualifying)
        qualifying_count = len(qualifying)
        percentage = round((attended / qualifying_count) * 100, 2) if qualifying_count else 0.0
        department_ids = {item[5].department_id for item in student_records}
        class_ids = {item[5].id for item in student_records}
        section_ids = {item[4].id for item in student_records}
        subject_ids = {item[3].id for item in student_records}
        result.append(
            AttendanceReportRow(
                student_id=student.id,
                student_number=student.student_number,
                student_name=f"{student.first_name} {student.last_name}",
                department_id=next(iter(department_ids)),
                class_id=next(iter(class_ids)),
                section_id=next(iter(section_ids)),
                subject_id=next(iter(subject_ids)) if len(subject_ids) == 1 else None,
                attended_sessions=attended,
                qualifying_sessions=qualifying_count,
                attendance_percentage=percentage,
            )
        )
    return sorted(result, key=lambda row: row.student_id)


def low_attendance(db: Session, user: User, filters: ReportFilters) -> list[LowAttendanceRow]:
    rows = _rows(db, user, filters)
    return [LowAttendanceRow(**row.model_dump()) for row in rows if row.attendance_percentage < filters.threshold]


def student_report(db: Session, user: User, student_id: int, filters: ReportFilters) -> list[AttendanceReportRow]:
    if user.role == UserRole.STUDENT:
        if user.student_profile is None or user.student_profile.id != student_id:
            raise not_allowed("Students can only view their own report")
    elif user.role not in {UserRole.ADMIN, UserRole.FACULTY}:
        raise not_allowed("You cannot access this report")
    return _rows(db, user, filters, fixed_student_id=student_id)


def section_report(db: Session, user: User, section_id: int, filters: ReportFilters) -> list[AttendanceReportRow]:
    return _rows(db, user, filters, fixed_section_id=section_id)


def subject_report(db: Session, user: User, subject_id: int, filters: ReportFilters) -> list[AttendanceReportRow]:
    return _rows(db, user, filters, fixed_subject_id=subject_id)
