from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Chart(Base, TimestampMixin):
    __tablename__ = "charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("analysis_sessions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    chart_type: Mapped[str] = mapped_column(String(50))
    config: Mapped[dict] = mapped_column(JSON, insert_default=lambda: {})
    image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="charts")
    session: Mapped[Optional[AnalysisSession]] = relationship(
        "AnalysisSession", back_populates="charts"
    )
