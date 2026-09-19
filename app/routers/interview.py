from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime
from ..schemas.common import DeleteResponse

from ..core.dependencies import get_current_user, get_db
from ..models import Application, Interview, User
from ..schemas.interview import (
    InterviewCreate,
    InterviewUpdate,
    InterviewResponse,
)

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
)


@router.post(
    "/",
    response_model=InterviewResponse,
    status_code=201,
)
def create_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.scalar(
        select(Application).where(
            Application.id == interview.application_id,
            Application.user_id == current_user.id,
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    new_interview = Interview(
        application_id=interview.application_id,
        round=interview.round,
        interview_date=interview.interview_date,
        notes=interview.notes,
        result=interview.result,
    )

    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    return new_interview


@router.get(
    "",
    response_model=list[InterviewResponse],
)
def get_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .where(
            Application.user_id == current_user.id,
        )
    )

    return db.scalars(query).all()

@router.get(
    "/upcoming",
    response_model=list[InterviewResponse],
)
def get_upcoming_interviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .where(
            Application.user_id == current_user.id,
            Interview.interview_date.is_not(None),
            Interview.interview_date >= datetime.now(),
        )
        .order_by(
            Interview.interview_date.asc()
        )
    )

    return db.scalars(query).all()

@router.get(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.scalar(
        select(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .where(
            Interview.id == interview_id,
            Application.user_id == current_user.id,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    return interview


@router.put(
    "/{interview_id}",
    response_model=InterviewResponse,
)
def update_interview(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.scalar(
        select(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .where(
            Interview.id == interview_id,
            Application.user_id == current_user.id,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    update_data = interview_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(interview, field, value)

    db.commit()
    db.refresh(interview)

    return interview


@router.delete(
    "/{interview_id}",
    response_model=DeleteResponse,
    status_code=200,
)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview = db.scalar(
        select(Interview)
        .join(
            Application,
            Interview.application_id == Application.id,
        )
        .where(
            Interview.id == interview_id,
            Application.user_id == current_user.id,
        )
    )

    if interview is None:
        raise HTTPException(
            status_code=404,
            detail="Interview not found",
        )

    db.delete(interview)
    db.commit()

    return {
    "message": "Interview deleted successfully",
    "id": interview_id,
}