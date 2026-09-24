# Edumerge Smart Attendance Management

## 1. Problem Understanding

The system manages attendance across academic departments, classes, sections, subjects, faculty assignments, and enrolled students. It must support reliable attendance recording, correction review, history, reporting, and identification of low-attendance students while enforcing role-based access.

## 2. Solution Overview

The application provides separate Admin, Faculty, and Student workspaces:

- Admin manages academic records, users, enrollments, assignments, corrections, and reports.
- Faculty creates attendance sessions, records attendance, submits sessions, and requests corrections.
- Students view their own attendance summaries, subject performance, history, and profile.

Backend authorization remains authoritative; the frontend provides role-aware navigation and protected routes for usability.

## 3. User Roles

- **Admin:** manages academic data and reviews correction requests and reports.
- **Faculty:** accesses only owned assignments and sections, manages attendance sessions, and submits correction requests.
- **Student:** accesses only their own profile, attendance summary, percentage, and history.

## 4. Main Workflows

1. Admin creates departments, classes, sections, subjects, faculty, and students.
2. Admin enrolls students and assigns faculty to subjects and sections.
3. Faculty creates a dated attendance session with an optional topic.
4. Faculty marks students as `PRESENT`, `ABSENT`, `LATE`, or `EXCUSED`, saves, and submits attendance.
5. Submitted or locked sessions become read-only for normal faculty editing.
6. Faculty requests corrections with a mandatory reason.
7. Admin approves or rejects corrections, optionally recording a review comment.
8. Students view overall, subject-wise, and historical attendance.

## 5. Architecture and Technology Choices

- **Backend:** FastAPI with SQLAlchemy, Pydantic schemas, and Alembic migrations.
- **Frontend:** React with React Router and Axios.
- **Database:** PostgreSQL for production-like relational integrity.
- **Authentication:** JWT bearer tokens with role-based dependencies.
- **Password security:** Argon2 hashing through the existing password utility.
- **Frontend state:** local React state and context; no additional state-management library was needed.

The implementation reuses shared layouts, API clients, form components, tables, feedback messages, and loading states to keep the application consistent.

## 6. Database Design

The schema separates authentication users from faculty and student profiles. Academic entities include departments, classes, sections, subjects, enrollments, and faculty assignments. Attendance is represented by sessions and student records. Correction requests reference attendance records and reviewer/requester users. Audit logs record important administrative and attendance actions.

Foreign keys protect relationships, while unique constraints prevent duplicate usernames, emails, student numbers, employee numbers, enrollments, assignments, sessions per assignment/date, and attendance records per session/student.

## 7. Authorization and Security

Authentication validates active users and JWT signatures, expiration, and identity. Role dependencies restrict Admin, Faculty, and Student APIs. Faculty ownership checks prevent access to other faculty assignments, sessions, or students outside assigned sections. Student endpoints use authenticated `me` scopes where possible and reject another student’s ID.

Passwords are never returned by API schemas and are stored as hashes. Environment files are ignored by Git. The development Admin seed is a local CLI mechanism and is explicitly intended for development credentials only.

## 8. Attendance and Correction Logic

Attendance sessions begin as `OPEN`, become `SUBMITTED` after all active enrolled students have records, and may later become `LOCKED` by an Admin. Normal updates are rejected after submission or locking. Duplicate records are prevented both by request validation and database constraints.

Corrections are allowed for submitted or locked sessions. A correction must change the existing status and include a reason. Only one pending correction is allowed for a record. Approval updates the attendance record; rejection leaves it unchanged. Correction actions are audited.

## 9. Reports and Low Attendance

The backend calculates attendance percentages and supplies report data for Admin, Faculty, and Student use cases. `PRESENT` and `LATE` count as attended sessions. `ABSENT` contributes to the qualifying denominator, while `EXCUSED` is excluded from the denominator. The default low-attendance threshold is 75%, and Admin reports support threshold and date filters.

Reports include low-attendance, section, subject, and student scopes. Student access is restricted to the authenticated student’s own data.

## 10. Important Assumptions

- An active enrollment identifies the students expected in a section.
- Faculty assignments, sections, and subjects must be active before new sessions can be created.
- The backend is the source of truth for role authorization and attendance calculations.
- The development seed credentials are suitable only for local evaluation.
- Faculty and Student accounts are created by an Admin through the management workflow.

## 11. Important Edge Cases

The system handles invalid credentials, inactive users, missing or invalid JWTs, unauthorized roles, missing attendance records, duplicate records, duplicate sessions, inactive academic resources, duplicate enrollments and assignments, missing correction reasons, duplicate pending corrections, already processed corrections, and attempts to edit submitted or locked sessions.

The frontend also provides loading, empty, success, and API error states for the main workflows.

## 12. Validation and Testing

Validation included:

- Complete backend test suite: 30 tests passed.
- Frontend production builds passed with Vite.
- API authentication and role authorization testing.
- Admin, Faculty, and Student end-to-end workflows.
- Attendance creation, saving, submission, history, and correction workflows.
- Admin correction approval and rejection through the UI.
- Low-attendance, section, subject, and student report verification.
- Student isolation and protection from Admin and Faculty management routes.

## 13. Engineering Trade-offs

The solution favors a conventional layered FastAPI/SQLAlchemy backend and focused React pages over additional abstractions or state libraries. Backend-calculated metrics avoid conflicting frontend calculations. Shared components reduce duplication, while the frontend remains intentionally lightweight for the assignment scope.

The current JWT client stores the access token in browser storage for simplicity. Production deployment should use a strong environment-managed JWT secret and consider more hardened token storage. The Admin corrections and reports interfaces were implemented using existing APIs without introducing new backend architecture.

## 14. AI Usage Report

GitHub Copilot and ChatGPT were used for architecture discussion, code generation, implementation assistance, testing and debugging assistance, and documentation.

AI-generated output was manually reviewed and validated through automated backend tests, frontend builds, API testing, authorization testing, and end-to-end workflows. The final implementation was adjusted to match the existing repository structure, backend contracts, security boundaries, and assignment requirements.
