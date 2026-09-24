from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser
from app.core.database import get_db
from app.schemas.report import AttendanceReportRow, LowAttendanceRow, ReportFilters
from app.services.report_service import low_attendance, section_report, student_report, subject_report

router = APIRouter(prefix="/reports")


def build_report_filters(
    filter_department_id: int | None = Query(default=None, gt=0, alias="department_id"),
    filter_class_id: int | None = Query(default=None, gt=0, alias="class_id"),
    filter_section_id: int | None = Query(default=None, gt=0, alias="section_id"),
    filter_subject_id: int | None = Query(default=None, gt=0, alias="subject_id"),
    filter_student_id: int | None = Query(default=None, gt=0, alias="student_id"),
    start_date: date | None = None,
    end_date: date | None = None,
    threshold: float = Query(default=75.0, ge=0, le=100),
) -> ReportFilters:
    return ReportFilters(
        department_id=filter_department_id,
        class_id=filter_class_id,
        section_id=filter_section_id,
        subject_id=filter_subject_id,
        student_id=filter_student_id,
        start_date=start_date,
        end_date=end_date,
        threshold=threshold,
    )


ReportQuery = Annotated[ReportFilters, Depends(build_report_filters)]


@router.get("/low-attendance", response_model=list[LowAttendanceRow])
def get_low_attendance_report(
    current_user: CurrentUser,
    filters: ReportQuery,
    db: Session = Depends(get_db),
):
    return low_attendance(db, current_user, filters)


@router.get("/students/{student_id}/attendance", response_model=list[AttendanceReportRow])
def get_student_attendance_report(
    student_id: int,
    current_user: CurrentUser,
    filters: ReportQuery,
    db: Session = Depends(get_db),
):
    return student_report(db, current_user, student_id, filters)


@router.get("/sections/{section_id}/attendance", response_model=list[AttendanceReportRow])
def get_section_attendance_report(
    section_id: int,
    current_user: CurrentUser,
    filters: ReportQuery,
    db: Session = Depends(get_db),
):
    return section_report(db, current_user, section_id, filters)


@router.get("/subjects/{subject_id}/attendance", response_model=list[AttendanceReportRow])
def get_subject_attendance_report(
    subject_id: int,
    current_user: CurrentUser,
    filters: ReportQuery,
    db: Session = Depends(get_db),
):
    return subject_report(db, current_user, subject_id, filters)
