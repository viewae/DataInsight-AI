from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AnalysisSession(Base, TimestampMixin):
    __tablename__ = "analysis_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    dataset_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("datasets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    conversation_history: Mapped[list] = mapped_column(JSON, insert_default=lambda: [])
    generated_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="sessions")
    project: Mapped[Optional[Project]] = relationship("Project", back_populates="sessions")
    dataset: Mapped[Optional[Dataset]] = relationship("Dataset", back_populates="sessions")
    charts: Mapped[list[Chart]] = relationship(
        "Chart", back_populates="session", cascade="all, delete-orphan"
    )
