from pydantic import BaseModel, Field


class DatasetOut(BaseModel):
    id: int
    name: str
    source_type: str
    row_count: int
    columns_meta: list

    model_config = {"from_attributes": True}


class DatasetPreviewResponse(BaseModel):
    columns: list[str]
    rows: list[dict]
