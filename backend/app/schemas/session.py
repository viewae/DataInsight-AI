from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    dataset_id: int
    title: Optional[str] = None


class SessionOut(BaseModel):
    id: int
    dataset_id: Optional[int]
    title: Optional[str]
    conversation_history: list
    generated_code: Optional[str]
    result_data: Optional[dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class SessionQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)


class SessionQueryResponse(BaseModel):
    answer: str
    model: str
    chart_suggestions: Optional[list] = None
