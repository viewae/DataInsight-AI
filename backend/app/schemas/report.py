from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportCreate(BaseModel):
    session_id: int
    title: Optional[str] = None


class ReportOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    share_token: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
