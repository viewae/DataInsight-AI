from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChartOut(BaseModel):
    id: int
    session_id: Optional[int]
    chart_type: str
    config: dict
    image_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
