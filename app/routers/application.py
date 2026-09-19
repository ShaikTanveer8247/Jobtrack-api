from ..core.dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, case, or_, asc, desc
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import (
    Application as ApplicationModel,
    ApplicationStatusHistory,
    User,
)
from ..schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    DashboardResponse,
    StatusHistoryResponse,
)
from ..schemas.status import ApplicationStatus
from ..schemas.common import DeleteResponse

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)





# -------------------------
# Routes
# -------------------------
@router.get(
    "",
    response_model=list[ApplicationResponse]
)
def get_applications(
    status: ApplicationStatus | None = Query(default=None),
    company: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
    ),
    role: str | None = Query(
        default=None,
        min_length=1,
        max_length=100
    ),
    search: str | None = Query(
        default=None,
        min_length=1,
        max_length=100,
    ),
    sort_by: str = Query(
        default="id",
        pattern="^(id|company|role|status|created_at|updated_at)$"
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100
    ),
    offset: int = Query(
        default=0,
        ge=0
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(ApplicationModel).where(
        ApplicationModel.user_id == current_user.id
    )

    if status:
        query = query.where(
            ApplicationModel.status == status
        )

    if company:
        query = query.where(
            ApplicationModel.company == company
        )

    if role:
        query = query.where(
            ApplicationModel.role == role
        )

    if search:
        search_pattern = f"%{search}%"

        query = query.where(
            or_(
                ApplicationModel.company.ilike(search_pattern),
                ApplicationModel.role.ilike(search_pattern),
            )
        )

    sort_column = getattr(
        ApplicationModel,
        sort_by,
    )

    if sort_order == "desc":
        query = query.order_by(
            desc(sort_column)
        )
    else:
        query = query.order_by(
            asc(sort_column)
        )

    query = query.offset(offset).limit(limit)

    applications = db.scalars(query).all()

    return applications

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stats = db.execute(
        select(
            func.count(ApplicationModel.id).label("total_applications"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            ApplicationModel.status
                            == ApplicationStatus.APPLIED.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("applied"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            ApplicationModel.status
                            == ApplicationStatus.INTERVIEW.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("interview"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            ApplicationModel.status
                            == ApplicationStatus.REJECTED.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("rejected"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            ApplicationModel.status
                            == ApplicationStatus.OFFER.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("offer"),

            func.coalesce(
                func.sum(
                    case(
                        (
                            ApplicationModel.status
                            == ApplicationStatus.ACCEPTED.value,
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("accepted"),
        )
        .where(
            ApplicationModel.user_id == current_user.id
        )
    ).one()

    recent_applications = db.scalars(
        select(ApplicationModel)
        .where(
            ApplicationModel.user_id == current_user.id
        )
        .order_by(
            ApplicationModel.updated_at.desc()
        )
        .limit(5)
    ).all()

    recent_application_responses = [
        ApplicationResponse.model_validate(application)
        for application in recent_applications
    ]

    return DashboardResponse(
        total_applications=stats.total_applications,
        applied=stats.applied,
        interview=stats.interview,
        rejected=stats.rejected,
        offer=stats.offer,
        accepted=stats.accepted,
        recent_applications=recent_application_responses,
    )
@router.get(
    "/{application_id}/history",
    response_model=list[StatusHistoryResponse],
)
def get_application_history(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.scalar(
        select(ApplicationModel).where(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id,
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    history = db.scalars(
        select(ApplicationStatusHistory)
        .where(
            ApplicationStatusHistory.application_id == application_id
        )
        .order_by(ApplicationStatusHistory.changed_at.asc())
    ).all()

    return history

@router.get(
    "/{application_id}",
    response_model=ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.scalar(
    select(ApplicationModel).where(
        ApplicationModel.id == application_id,
        ApplicationModel.user_id == current_user.id,
    )
)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application
@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_application = ApplicationModel(
        user_id=current_user.id,
        company=application.company,
        role=application.role,
        status=application.status,
    )

    db.add(new_application)

    try:
        db.flush()

        status_history = ApplicationStatusHistory(
            application_id=new_application.id,
            old_status=None,
            new_status=application.status.value,
        )

        db.add(status_history)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An application for this company and role already exists for this user",
        )

    db.refresh(new_application)

    return new_application

@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: int,
    application: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_application = db.scalar(
        select(ApplicationModel).where(
            ApplicationModel.id == application_id,
            ApplicationModel.user_id == current_user.id,
        )
    )

    if existing_application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found",
        )

    update_data = application.model_dump(
        exclude_unset=True
    )

    old_status = existing_application.status

    for field, value in update_data.items():
        setattr(existing_application, field, value)

    status_changed = (
        "status" in update_data
        and update_data["status"] != old_status
    )

    if status_changed:
        new_status = update_data["status"]

        if isinstance(new_status, ApplicationStatus):
            new_status = new_status.value

        status_history = ApplicationStatusHistory(
            application_id=existing_application.id,
            old_status=old_status,
            new_status=new_status,
        )

        db.add(status_history)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An application for this company and role already exists for this user",
        )

    db.refresh(existing_application)

    return existing_application


@router.delete(
    "/{application_id}",
    response_model=DeleteResponse,
    status_code=200,
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    application = db.scalar(
    select(ApplicationModel).where(
        ApplicationModel.id == application_id,
        ApplicationModel.user_id == current_user.id,
    )
)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return {
    "message": "Application deleted successfully",
    "id": application_id,
}