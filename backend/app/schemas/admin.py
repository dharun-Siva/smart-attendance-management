from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=30)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    code: str | None = Field(default=None, min_length=1, max_length=30)
    is_active: bool | None = None


class DepartmentResponse(ORMModel):
    id: int
    name: str
    code: str
    is_active: bool


class ClassCreate(BaseModel):
    department_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=30)


class ClassUpdate(BaseModel):
    department_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    code: str | None = Field(default=None, min_length=1, max_length=30)
    is_active: bool | None = None


class ClassResponse(ORMModel):
    id: int
    department_id: int
    name: str
    code: str
    is_active: bool


class SectionCreate(BaseModel):
    class_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)


class SectionUpdate(BaseModel):
    class_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class SectionResponse(ORMModel):
    id: int
    class_id: int
    name: str
    is_active: bool


class SubjectCreate(BaseModel):
    department_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=30)


class SubjectUpdate(BaseModel):
    department_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    code: str | None = Field(default=None, min_length=1, max_length=30)
    is_active: bool | None = None


class SubjectResponse(ORMModel):
    id: int
    department_id: int
    name: str
    code: str
    is_active: bool


class AccountCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    department_id: int = Field(gt=0)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class AccountUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=1, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    department_id: int | None = Field(default=None, gt=0)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class FacultyCreate(AccountCreate):
    employee_number: str = Field(min_length=1, max_length=50)


class FacultyUpdate(AccountUpdate):
    employee_number: str | None = Field(default=None, min_length=1, max_length=50)


class FacultyResponse(ORMModel):
    id: int
    user_id: int
    username: str
    email: str
    department_id: int
    employee_number: str
    first_name: str
    last_name: str
    is_active: bool


class StudentCreate(AccountCreate):
    student_number: str = Field(min_length=1, max_length=50)


class StudentUpdate(AccountUpdate):
    student_number: str | None = Field(default=None, min_length=1, max_length=50)


class StudentResponse(ORMModel):
    id: int
    user_id: int
    username: str
    email: str
    department_id: int
    student_number: str
    first_name: str
    last_name: str
    is_active: bool


class EnrollmentCreate(BaseModel):
    student_id: int = Field(gt=0)
    section_id: int = Field(gt=0)


class EnrollmentUpdate(BaseModel):
    section_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class EnrollmentResponse(ORMModel):
    id: int
    student_id: int
    section_id: int
    is_active: bool


class AssignmentCreate(BaseModel):
    faculty_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    section_id: int = Field(gt=0)


class AssignmentUpdate(BaseModel):
    faculty_id: int | None = Field(default=None, gt=0)
    subject_id: int | None = Field(default=None, gt=0)
    section_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class AssignmentResponse(ORMModel):
    id: int
    faculty_id: int
    subject_id: int
    section_id: int
    is_active: bool
