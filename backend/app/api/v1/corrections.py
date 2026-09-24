from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import AdminUser, CurrentUser, FacultyUser
from app.core.database import get_db
from app.schemas.correction import CorrectionCreate, CorrectionResponse, CorrectionReview
from app.services.correction_service import (
    correction_response,
    get_correction,
    list_corrections,
    request_correction,
    review_correction,
)

router = APIRouter()


@router.post(
    "/attendance/records/{record_id}/corrections",
    response_model=CorrectionResponse,
    status_code=201,
)
def create_correction(
    record_id: int,
    payload: CorrectionCreate,
    faculty: FacultyUser,
    db: Session = Depends(get_db),
):
    return correction_response(request_correction(db, faculty, record_id, payload))


@router.get("/corrections", response_model=list[CorrectionResponse])
def get_corrections(current_user: CurrentUser, db: Session = Depends(get_db)):
    return [correction_response(item) for item in list_corrections(db, current_user)]


@router.get("/corrections/{correction_id}", response_model=CorrectionResponse)
def get_correction_by_id(
    correction_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return correction_response(get_correction(db, current_user, correction_id))


@router.post("/corrections/{correction_id}/approve", response_model=CorrectionResponse)
def approve_correction(
    correction_id: int,
    admin: AdminUser,
    payload: CorrectionReview | None = None,
    db: Session = Depends(get_db),
):
    return correction_response(review_correction(db, admin, correction_id, payload or CorrectionReview(), True))


@router.post("/corrections/{correction_id}/reject", response_model=CorrectionResponse)
def reject_correction(
    correction_id: int,
    admin: AdminUser,
    payload: CorrectionReview | None = None,
    db: Session = Depends(get_db),
):
    return correction_response(review_correction(db, admin, correction_id, payload or CorrectionReview(), False))
