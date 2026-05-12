import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Dataset, User
from app.schemas.dataset import DatasetOut, DatasetPreviewResponse
from app.services.dataset_io import ALLOWED_EXTENSIONS, _read_meta, load_preview_records, safe_resolve

router = APIRouter()


def _ensure_upload_root() -> Path:
    root = Path(settings.UPLOAD_DIR)
    root.mkdir(parents=True, exist_ok=True)
    return root


@router.post("/upload", response_model=DatasetOut)
async def upload(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少文件名")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"仅支持: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件超过 {settings.MAX_UPLOAD_MB} MB 上限",
        )

    row_count, columns_meta = await run_in_threadpool(_read_meta, content, suffix)

    token = secrets.token_hex(8)
    safe_name = f"{token}{suffix}"
    user_dir = _ensure_upload_root() / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    dest = user_dir / safe_name
    dest.write_bytes(content)

    relative = f"{user.id}/{safe_name}"
    display_name = (name or Path(file.filename).stem).strip() or safe_name

    ds = Dataset(
        user_id=user.id,
        name=display_name[:255],
        source_type="upload",
        file_path=relative,
        row_count=row_count,
        columns_meta=columns_meta,
    )
    db.add(ds)
    await db.commit()
    await db.refresh(ds)
    return DatasetOut.model_validate(ds)


@router.post("/connect-db")
async def connect_db():
    return {"message": "stub", "path": "POST /api/dataset/connect-db"}


async def _get_user_dataset(db: AsyncSession, user_id: int, dataset_id: int) -> Dataset:
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    ds = result.scalar_one_or_none()
    if ds is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据集不存在")
    return ds


@router.get("/{dataset_id}/preview", response_model=DatasetPreviewResponse)
async def preview(
    dataset_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _get_user_dataset(db, user.id, dataset_id)
    try:
        columns, rows = await run_in_threadpool(
            load_preview_records,
            ds.file_path,
            settings.PREVIEW_MAX_ROWS,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件已丢失",
        ) from None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return DatasetPreviewResponse(columns=columns, rows=rows)


@router.get("/{dataset_id}/schema")
async def schema(
    dataset_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _get_user_dataset(db, user.id, dataset_id)
    return {"dataset_id": ds.id, "columns": ds.columns_meta}


@router.get("/list", response_model=list[DatasetOut])
async def list_datasets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Dataset).where(Dataset.user_id == user.id).order_by(Dataset.created_at.desc())
    )
    return [DatasetOut.model_validate(ds) for ds in result.scalars().all()]


@router.get("/{dataset_id}", response_model=DatasetOut)
async def get_dataset(
    dataset_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await db.get(Dataset, dataset_id)
    if ds is None or ds.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据集不存在")
    return DatasetOut.model_validate(ds)


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await _get_user_dataset(db, user.id, dataset_id)
    try:
        path = safe_resolve(Path(settings.UPLOAD_DIR), ds.file_path)
        if path.is_file():
            path.unlink(missing_ok=True)
    except PermissionError:
        pass
    await db.delete(ds)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
