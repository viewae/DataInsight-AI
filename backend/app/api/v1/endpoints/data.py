from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Optional
import pandas as pd

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Dataset, User
from app.services.dataset_io import read_full_dataframe
from app.core.config import settings

router = APIRouter()


class CleanRequest(BaseModel):
    dataset_id: int
    drop_na: bool = False
    drop_duplicates: bool = False
    fill_na: Optional[dict[str, Any]] = None


class TransformRequest(BaseModel):
    dataset_id: int
    filter_column: Optional[str] = None
    filter_value: Optional[str] = None
    group_by: Optional[str] = None
    agg_column: Optional[str] = None
    agg_func: Optional[str] = None  # sum, mean, count, min, max


class StatsResponse(BaseModel):
    dataset_id: int
    columns: list[str]
    stats: dict[str, Any]  # per-column statistics


async def _load_dataset(db: AsyncSession, user_id: int, dataset_id: int) -> Dataset:
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    ds = result.scalar_one_or_none()
    if ds is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据集不存在")
    return ds


@router.post("/clean")
async def clean(
    body: CleanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _load_dataset(db, user.id, body.dataset_id)
    df = await run_in_threadpool(read_full_dataframe, ds.file_path)

    original = len(df)
    if body.drop_na:
        df = df.dropna()
    if body.drop_duplicates:
        df = df.drop_duplicates()
    if body.fill_na and isinstance(body.fill_na, dict):
        df = df.fillna(body.fill_na)

    remaining = len(df)
    columns = [str(c) for c in df.columns]
    rows = df.fillna("").head(settings.PREVIEW_MAX_ROWS).to_dict(orient="records")

    return {
        "original_rows": original,
        "remaining_rows": remaining,
        "removed": original - remaining,
        "columns": columns,
        "preview": rows,
    }


@router.post("/transform")
async def transform(
    body: TransformRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _load_dataset(db, user.id, body.dataset_id)
    df = await run_in_threadpool(read_full_dataframe, ds.file_path)

    # filter
    if body.filter_column and body.filter_value:
        col = body.filter_column
        val = body.filter_value
        if col in df.columns:
            df = df[df[col].astype(str).str.contains(val, na=False)]

    # group by / aggregate
    if body.group_by and body.agg_column and body.agg_func:
        func_map = {"sum": "sum", "mean": "mean", "count": "count", "min": "min", "max": "max"}
        agg = func_map.get(body.agg_func, "sum")
        try:
            df = df.groupby(body.group_by)[body.agg_column].agg(agg).reset_index()
        except Exception:
            pass

    columns = [str(c) for c in df.columns]
    rows = df.fillna("").head(settings.PREVIEW_MAX_ROWS).to_dict(orient="records")
    return {"columns": columns, "rows": rows, "total_rows": len(df)}


@router.get("/{dataset_id}/stats", response_model=StatsResponse)
async def stats(
    dataset_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _load_dataset(db, user.id, dataset_id)

    result = {}
    columns = [c["name"] for c in ds.columns_meta]

    for col_meta in ds.columns_meta:
        name = col_meta["name"]
        dtype = col_meta.get("dtype", "")
        if "int" in dtype or "float" in dtype:
            result[name] = {"type": "numeric", "stats": {}}
        elif "datetime" in dtype:
            result[name] = {"type": "datetime", "stats": {}}
        else:
            result[name] = {"type": "categorical", "stats": {"unique": "?"}}

    # compute actual stats from data
    try:
        df = await run_in_threadpool(
            _read_dataframe, ds.file_path, ds.source_type
        )
        for col in df.select_dtypes(include=["number"]).columns:
            result[str(col)]["stats"] = {
                "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                "std": float(df[col].std()) if pd.notna(df[col].std()) else None,
                "missing": int(df[col].isna().sum()),
            }
        for col in df.select_dtypes(exclude=["number"]).columns:
            result[str(col)]["stats"] = {
                "unique": int(df[col].nunique()),
                "missing": int(df[col].isna().sum()),
            }
    except Exception:
        pass

    return StatsResponse(dataset_id=ds.id, columns=columns, stats=result)
