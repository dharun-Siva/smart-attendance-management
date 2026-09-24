from typing import Callable, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import AdminUser
from app.core.database import get_db
from app.core.security import hash_password
from app.models.assignment import FacultyAssignment
from app.models.audit import AuditLog
from app.models.class_section import Class as ClassModel
from app.models.class_section import Section
from app.models.department import Department
from app.models.enrollment import StudentEnrollment
from app.models.enums import UserRole
from app.models.faculty import FacultyProfile
from app.models.student import StudentProfile
from app.models.subject import Subject
from app.models.user import User
from app.schemas.admin import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
    FacultyCreate,
    FacultyResponse,
    FacultyUpdate,
    SectionCreate,
    SectionResponse,
    SectionUpdate,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
)
from app.services.admin_service import add_audit, commit_or_conflict, conflict, flush_or_conflict, not_found

router = APIRouter()
ModelT = TypeVar("ModelT")


def get_or_404(db: Session, model: type[ModelT], entity_id: int, entity_name: str) -> ModelT:
    entity = db.get(model, entity_id)
    if entity is None:
        raise not_found(entity_name, entity_id)
    return entity


def active_or_404(entity: ModelT, entity_name: str, entity_id: int) -> ModelT:
    if not getattr(entity, "is_active", False):
        raise HTTPException(status_code=400, detail=f"{entity_name} with id {entity_id} is inactive")
    return entity


def audit_commit(
    db: Session,
    admin: User,
    action: str,
    entity_type: str,
    entity_id: int,
    description: str,
) -> None:
    add_audit(db, admin, action, entity_type, entity_id, description)
    commit_or_conflict(db)


def user_conflict_query(username: str | None, email: str | None):
    values = []
    if username is not None:
        values.append(User.username == username)
    if email is not None:
        values.append(User.email == email)
    return or_(*values)


def faculty_response(profile: FacultyProfile) -> FacultyResponse:
    return FacultyResponse(
        id=profile.id,
        user_id=profile.user_id,
        username=profile.user.username,
        email=profile.user.email,
        department_id=profile.department_id,
        employee_number=profile.employee_number,
        first_name=profile.first_name,
        last_name=profile.last_name,
        is_active=profile.user.is_active,
    )


def student_response(profile: StudentProfile) -> StudentResponse:
    return StudentResponse(
        id=profile.id,
        user_id=profile.user_id,
        username=profile.user.username,
        email=profile.user.email,
        department_id=profile.department_id,
        student_number=profile.student_number,
        first_name=profile.first_name,
        last_name=profile.last_name,
        is_active=profile.user.is_active,
    )


# Departments
@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(Department).order_by(Department.id)).all())


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, admin: AdminUser, db: Session = Depends(get_db)):
    if db.scalar(select(Department).where(or_(Department.name == payload.name, Department.code == payload.code))):
        raise conflict("Department name or code already exists")
    department = Department(name=payload.name, code=payload.code)
    db.add(department)
    db.flush()
    audit_commit(db, admin, "CREATE", "department", department.id, f"Created department {department.code}")
    return department


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return get_or_404(db, Department, department_id, "Department")


@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, payload: DepartmentUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    department = get_or_404(db, Department, department_id, "Department")
    values = payload.model_dump(exclude_unset=True)
    if values.get("name") is not None or values.get("code") is not None:
        duplicate = db.scalar(
            select(Department).where(
                Department.id != department_id,
                or_(
                    Department.name == values.get("name", department.name),
                    Department.code == values.get("code", department.code),
                ),
            )
        )
        if duplicate:
            raise conflict("Department name or code already exists")
    for field, value in values.items():
        setattr(department, field, value)
    audit_commit(db, admin, "UPDATE", "department", department.id, f"Updated department {department.code}")
    return department


# Classes
@router.get("/classes", response_model=list[ClassResponse])
def list_classes(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(ClassModel).order_by(ClassModel.id)).all())


@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(payload: ClassCreate, admin: AdminUser, db: Session = Depends(get_db)):
    department = get_or_404(db, Department, payload.department_id, "Department")
    active_or_404(department, "Department", payload.department_id)
    item = ClassModel(**payload.model_dump())
    db.add(item)
    db.flush()
    audit_commit(db, admin, "CREATE", "class", item.id, f"Created class {item.code}")
    return item


@router.get("/classes/{class_id}", response_model=ClassResponse)
def get_class(class_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return get_or_404(db, ClassModel, class_id, "Class")


@router.patch("/classes/{class_id}", response_model=ClassResponse)
def update_class(class_id: int, payload: ClassUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, ClassModel, class_id, "Class")
    values = payload.model_dump(exclude_unset=True)
    if values.get("department_id") is not None:
        department = get_or_404(db, Department, values["department_id"], "Department")
        active_or_404(department, "Department", values["department_id"])
    for field, value in values.items():
        setattr(item, field, value)
    audit_commit(db, admin, "UPDATE", "class", item.id, f"Updated class {item.code}")
    return item


# Sections
@router.get("/sections", response_model=list[SectionResponse])
def list_sections(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(Section).order_by(Section.id)).all())


@router.post("/sections", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
def create_section(payload: SectionCreate, admin: AdminUser, db: Session = Depends(get_db)):
    class_item = get_or_404(db, ClassModel, payload.class_id, "Class")
    active_or_404(class_item, "Class", payload.class_id)
    if db.scalar(select(Section).where(Section.class_id == payload.class_id, Section.name == payload.name)):
        raise conflict("Section name already exists in this class")
    item = Section(**payload.model_dump())
    db.add(item)
    db.flush()
    audit_commit(db, admin, "CREATE", "section", item.id, f"Created section {item.name}")
    return item


@router.get("/sections/{section_id}", response_model=SectionResponse)
def get_section(section_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return get_or_404(db, Section, section_id, "Section")


@router.patch("/sections/{section_id}", response_model=SectionResponse)
def update_section(section_id: int, payload: SectionUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, Section, section_id, "Section")
    values = payload.model_dump(exclude_unset=True)
    target_class_id = values.get("class_id", item.class_id)
    class_item = get_or_404(db, ClassModel, target_class_id, "Class")
    active_or_404(class_item, "Class", target_class_id)
    target_name = values.get("name", item.name)
    duplicate = db.scalar(
        select(Section).where(
            Section.id != section_id,
            Section.class_id == target_class_id,
            Section.name == target_name,
        )
    )
    if duplicate:
        raise conflict("Section name already exists in this class")
    for field, value in values.items():
        setattr(item, field, value)
    audit_commit(db, admin, "UPDATE", "section", item.id, f"Updated section {item.name}")
    return item


# Subjects
@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(Subject).order_by(Subject.id)).all())


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate, admin: AdminUser, db: Session = Depends(get_db)):
    department = get_or_404(db, Department, payload.department_id, "Department")
    active_or_404(department, "Department", payload.department_id)
    item = Subject(**payload.model_dump())
    db.add(item)
    db.flush()
    audit_commit(db, admin, "CREATE", "subject", item.id, f"Created subject {item.code}")
    return item


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def get_subject(subject_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return get_or_404(db, Subject, subject_id, "Subject")


@router.patch("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(subject_id: int, payload: SubjectUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, Subject, subject_id, "Subject")
    values = payload.model_dump(exclude_unset=True)
    if values.get("department_id") is not None:
        department = get_or_404(db, Department, values["department_id"], "Department")
        active_or_404(department, "Department", values["department_id"])
    for field, value in values.items():
        setattr(item, field, value)
    audit_commit(db, admin, "UPDATE", "subject", item.id, f"Updated subject {item.code}")
    return item


# Faculty and students
@router.get("/faculty", response_model=list[FacultyResponse])
def list_faculty(_: AdminUser, db: Session = Depends(get_db)):
    return [faculty_response(item) for item in db.scalars(select(FacultyProfile).order_by(FacultyProfile.id)).all()]


@router.post("/faculty", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
def create_faculty(payload: FacultyCreate, admin: AdminUser, db: Session = Depends(get_db)):
    department = get_or_404(db, Department, payload.department_id, "Department")
    active_or_404(department, "Department", payload.department_id)
    if db.scalar(select(User).where(user_conflict_query(payload.username, payload.email))):
        raise conflict("Username or email already exists")
    if db.scalar(select(FacultyProfile).where(FacultyProfile.employee_number == payload.employee_number)):
        raise conflict("Employee number already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.FACULTY,
    )
    profile = FacultyProfile(
        department_id=payload.department_id,
        employee_number=payload.employee_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        user=user,
    )
    db.add(profile)
    flush_or_conflict(db)
    add_audit(db, admin, "CREATE", "faculty_profile", profile.id, f"Created faculty {user.username}")
    commit_or_conflict(db)
    return faculty_response(profile)


@router.get("/faculty/{faculty_id}", response_model=FacultyResponse)
def get_faculty(faculty_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return faculty_response(get_or_404(db, FacultyProfile, faculty_id, "Faculty"))


@router.patch("/faculty/{faculty_id}", response_model=FacultyResponse)
def update_faculty(faculty_id: int, payload: FacultyUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    profile = get_or_404(db, FacultyProfile, faculty_id, "Faculty")
    user = profile.user
    values = payload.model_dump(exclude_unset=True)
    if "username" in values or "email" in values:
        duplicate = db.scalar(
            select(User).where(
                User.id != user.id,
                user_conflict_query(values.get("username", user.username), values.get("email", user.email)),
            )
        )
        if duplicate:
            raise conflict("Username or email already exists")
    if values.get("employee_number") is not None and db.scalar(
        select(FacultyProfile).where(
            FacultyProfile.id != faculty_id,
            FacultyProfile.employee_number == values["employee_number"],
        )
    ):
        raise conflict("Employee number already exists")
    if values.get("department_id") is not None:
        department = get_or_404(db, Department, values["department_id"], "Department")
        active_or_404(department, "Department", values["department_id"])
    for field in ("username", "email", "is_active"):
        if field in values:
            setattr(user, field, values[field])
    if values.get("password") is not None:
        user.password_hash = hash_password(values["password"])
    for field in ("department_id", "employee_number", "first_name", "last_name"):
        if field in values:
            setattr(profile, field, values[field])
    audit_commit(db, admin, "UPDATE", "faculty_profile", profile.id, f"Updated faculty {user.username}")
    return faculty_response(profile)


@router.get("/students", response_model=list[StudentResponse])
def list_students(_: AdminUser, db: Session = Depends(get_db)):
    return [student_response(item) for item in db.scalars(select(StudentProfile).order_by(StudentProfile.id)).all()]


@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, admin: AdminUser, db: Session = Depends(get_db)):
    department = get_or_404(db, Department, payload.department_id, "Department")
    active_or_404(department, "Department", payload.department_id)
    if db.scalar(select(User).where(user_conflict_query(payload.username, payload.email))):
        raise conflict("Username or email already exists")
    if db.scalar(select(StudentProfile).where(StudentProfile.student_number == payload.student_number)):
        raise conflict("Student number already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.STUDENT,
    )
    profile = StudentProfile(
        department_id=payload.department_id,
        student_number=payload.student_number,
        first_name=payload.first_name,
        last_name=payload.last_name,
        user=user,
    )
    db.add(profile)
    flush_or_conflict(db)
    add_audit(db, admin, "CREATE", "student_profile", profile.id, f"Created student {user.username}")
    commit_or_conflict(db)
    return student_response(profile)


@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return student_response(get_or_404(db, StudentProfile, student_id, "Student"))


@router.patch("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, payload: StudentUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    profile = get_or_404(db, StudentProfile, student_id, "Student")
    user = profile.user
    values = payload.model_dump(exclude_unset=True)
    if "username" in values or "email" in values:
        duplicate = db.scalar(
            select(User).where(
                User.id != user.id,
                user_conflict_query(values.get("username", user.username), values.get("email", user.email)),
            )
        )
        if duplicate:
            raise conflict("Username or email already exists")
    if values.get("student_number") is not None and db.scalar(
        select(StudentProfile).where(
            StudentProfile.id != student_id,
            StudentProfile.student_number == values["student_number"],
        )
    ):
        raise conflict("Student number already exists")
    if values.get("department_id") is not None:
        department = get_or_404(db, Department, values["department_id"], "Department")
        active_or_404(department, "Department", values["department_id"])
    for field in ("username", "email", "is_active"):
        if field in values:
            setattr(user, field, values[field])
    if values.get("password") is not None:
        user.password_hash = hash_password(values["password"])
    for field in ("department_id", "student_number", "first_name", "last_name"):
        if field in values:
            setattr(profile, field, values[field])
    audit_commit(db, admin, "UPDATE", "student_profile", profile.id, f"Updated student {user.username}")
    return student_response(profile)


# Enrollments
@router.get("/enrollments", response_model=list[EnrollmentResponse])
def list_enrollments(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(StudentEnrollment).order_by(StudentEnrollment.id)).all())


@router.post("/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(payload: EnrollmentCreate, admin: AdminUser, db: Session = Depends(get_db)):
    student = get_or_404(db, StudentProfile, payload.student_id, "Student")
    section = get_or_404(db, Section, payload.section_id, "Section")
    active_or_404(student.user, "Student account", student.id)
    active_or_404(section, "Section", section.id)
    if db.scalar(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == payload.student_id,
            StudentEnrollment.is_active.is_(True),
        )
    ):
        raise conflict("Student already has an active enrollment")
    if db.scalar(
        select(StudentEnrollment).where(
            StudentEnrollment.student_id == payload.student_id,
            StudentEnrollment.section_id == payload.section_id,
        )
    ):
        raise conflict("Enrollment already exists")
    item = StudentEnrollment(**payload.model_dump())
    db.add(item)
    db.flush()
    audit_commit(db, admin, "CREATE", "student_enrollment", item.id, "Created student enrollment")
    return item


@router.patch("/enrollments/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(enrollment_id: int, payload: EnrollmentUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, StudentEnrollment, enrollment_id, "Enrollment")
    values = payload.model_dump(exclude_unset=True)
    if values.get("section_id") is not None:
        section = get_or_404(db, Section, values["section_id"], "Section")
        active_or_404(section, "Section", values["section_id"])
        duplicate = db.scalar(
            select(StudentEnrollment).where(
                StudentEnrollment.id != enrollment_id,
                StudentEnrollment.student_id == item.student_id,
                StudentEnrollment.section_id == values["section_id"],
            )
        )
        if duplicate:
            raise conflict("Enrollment already exists")
    if values.get("is_active") is True and db.scalar(
        select(StudentEnrollment).where(
            StudentEnrollment.id != enrollment_id,
            StudentEnrollment.student_id == item.student_id,
            StudentEnrollment.is_active.is_(True),
        )
    ):
        raise conflict("Student already has an active enrollment")
    for field, value in values.items():
        setattr(item, field, value)
    audit_commit(db, admin, "UPDATE", "student_enrollment", item.id, "Updated student enrollment")
    return item


# Faculty assignments
@router.get("/assignments", response_model=list[AssignmentResponse])
def list_assignments(_: AdminUser, db: Session = Depends(get_db)):
    return list(db.scalars(select(FacultyAssignment).order_by(FacultyAssignment.id)).all())


@router.post("/assignments", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(payload: AssignmentCreate, admin: AdminUser, db: Session = Depends(get_db)):
    faculty = get_or_404(db, FacultyProfile, payload.faculty_id, "Faculty")
    subject = get_or_404(db, Subject, payload.subject_id, "Subject")
    section = get_or_404(db, Section, payload.section_id, "Section")
    active_or_404(faculty.user, "Faculty account", faculty.id)
    active_or_404(subject, "Subject", subject.id)
    active_or_404(section, "Section", section.id)
    if db.scalar(
        select(FacultyAssignment).where(
            FacultyAssignment.faculty_id == payload.faculty_id,
            FacultyAssignment.subject_id == payload.subject_id,
            FacultyAssignment.section_id == payload.section_id,
        )
    ):
        raise conflict("Faculty assignment already exists")
    item = FacultyAssignment(**payload.model_dump())
    db.add(item)
    db.flush()
    audit_commit(db, admin, "CREATE", "faculty_assignment", item.id, "Created faculty assignment")
    return item


@router.get("/assignments/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(assignment_id: int, _: AdminUser, db: Session = Depends(get_db)):
    return get_or_404(db, FacultyAssignment, assignment_id, "Assignment")


@router.patch("/assignments/{assignment_id}", response_model=AssignmentResponse)
def update_assignment(assignment_id: int, payload: AssignmentUpdate, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, FacultyAssignment, assignment_id, "Assignment")
    values = payload.model_dump(exclude_unset=True)
    faculty_id = values.get("faculty_id", item.faculty_id)
    subject_id = values.get("subject_id", item.subject_id)
    section_id = values.get("section_id", item.section_id)
    faculty = get_or_404(db, FacultyProfile, faculty_id, "Faculty")
    subject = get_or_404(db, Subject, subject_id, "Subject")
    section = get_or_404(db, Section, section_id, "Section")
    active_or_404(faculty.user, "Faculty account", faculty_id)
    active_or_404(subject, "Subject", subject_id)
    active_or_404(section, "Section", section_id)
    duplicate = db.scalar(
        select(FacultyAssignment).where(
            FacultyAssignment.id != assignment_id,
            FacultyAssignment.faculty_id == faculty_id,
            FacultyAssignment.subject_id == subject_id,
            FacultyAssignment.section_id == section_id,
        )
    )
    if duplicate:
        raise conflict("Faculty assignment already exists")
    for field, value in values.items():
        setattr(item, field, value)
    audit_commit(db, admin, "UPDATE", "faculty_assignment", item.id, "Updated faculty assignment")
    return item


@router.post("/assignments/{assignment_id}/deactivate", response_model=AssignmentResponse)
def deactivate_assignment(assignment_id: int, admin: AdminUser, db: Session = Depends(get_db)):
    item = get_or_404(db, FacultyAssignment, assignment_id, "Assignment")
    item.is_active = False
    audit_commit(db, admin, "DEACTIVATE", "faculty_assignment", item.id, "Deactivated faculty assignment")
    return item
