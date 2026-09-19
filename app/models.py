from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    UniqueConstraint,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

class Application(Base):
    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "company",
            "role",
            name="uq_application_user_company_role",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    company: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    round: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    interview_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Pending",
    )

class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applications.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    old_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )