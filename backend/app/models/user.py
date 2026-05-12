from __future__ import annotations

from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    quota_limit: Mapped[int] = mapped_column(Integer, default=10)
    quota_used: Mapped[int] = mapped_column(Integer, default=0)

    datasets: Mapped[list[Dataset]] = relationship(
        "Dataset", back_populates="user", cascade="all, delete-orphan"
    )
    projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    sessions: Mapped[list[AnalysisSession]] = relationship(
        "AnalysisSession", back_populates="user", cascade="all, delete-orphan"
    )
    charts: Mapped[list[Chart]] = relationship(
        "Chart", back_populates="user", cascade="all, delete-orphan"
    )
    reports: Mapped[list[Report]] = relationship(
        "Report", back_populates="user", cascade="all, delete-orphan"
    )
