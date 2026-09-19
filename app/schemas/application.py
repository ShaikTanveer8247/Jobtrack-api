from .status import ApplicationStatus
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class ApplicationCreate(BaseModel):
    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: ApplicationStatus

    @field_validator("company", "role")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty or contain only spaces")

        return value

class ApplicationResponse(BaseModel):
    id: int
    company: str
    role: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
class ApplicationUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=100)
    role: str | None = Field(default=None, min_length=1, max_length=100)
    status: ApplicationStatus | None = None

class DashboardResponse(BaseModel):
    total_applications: int
    applied: int
    interview: int
    rejected: int
    offer: int
    accepted: int
    recent_applications: list[ApplicationResponse]

class StatusHistoryResponse(BaseModel):
    id: int
    application_id: int
    old_status: str | None
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)