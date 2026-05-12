from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Dataset(Base, TimestampMixin):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(50))
    file_path: Mapped[str] = mapped_column(String(1024))
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    columns_meta: Mapped[list] = mapped_column(JSON, insert_default=lambda: [])

    user: Mapped[User] = relationship("User", back_populates="datasets")
    project: Mapped[Optional[Project]] = relationship("Project", back_populates="datasets")
    sessions: Mapped[list[AnalysisSession]] = relationship(
        "AnalysisSession", back_populates="dataset", cascade="all, delete-orphan"
    )
