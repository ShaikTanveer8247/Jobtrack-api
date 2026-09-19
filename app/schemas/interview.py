from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InterviewCreate(BaseModel):
    application_id: int = Field(gt=0)
    round: str = Field(min_length=1, max_length=50)
    interview_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=5000)
    result: str = Field(default="Pending", min_length=1, max_length=50)

    @field_validator("round")
    @classmethod
    def validate_round(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Round cannot be empty")

        return value

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Result cannot be empty")

        return value


class InterviewUpdate(BaseModel):
    round: str | None = Field(default=None, min_length=1, max_length=50)
    interview_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=5000)
    result: str | None = Field(default=None, min_length=1, max_length=50)

    @field_validator("round")
    @classmethod
    def validate_round(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Round cannot be empty")

        return value

    @field_validator("result")
    @classmethod
    def validate_result(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Result cannot be empty")

        return value


class InterviewResponse(BaseModel):
    id: int
    application_id: int
    round: str
    interview_date: datetime | None
    notes: str | None
    result: str

    model_config = ConfigDict(from_attributes=True)
    
