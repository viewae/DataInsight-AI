import pandas as pd
from pathlib import Path
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional

from app.core.config import settings
from app.models import Dataset
from app.services.dataset_io import load_preview_records


def _build_column_summaries(path: Path, columns: list[str]) -> str:
    """计算数值列的统计摘要，返回文本描述。"""
    try:
        df = pd.read_csv(path, nrows=settings.MAX_DATASET_PARSE_ROWS)
    except Exception:
        return ""
    parts = []
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            parts.append(
                f"  {col}: 数值列, 范围 {desc['min']:.2f}~{desc['max']:.2f}, "
                f"均值 {desc['mean']:.2f}, 中位数 {df[col].median():.2f}"
            )
        else:
            nunique = df[col].nunique()
            top_val = df[col].value_counts().index[0] if nunique > 0 else ""
            parts.append(
                f"  {col}: 文本列, {nunique} 个唯一值"
                + (f", 最常见「{top_val}」" if nunique <= 20 else "")
            )
    return "\n".join(parts)


async def build_dataset_context(
    db: AsyncSession,
    user_id: int,
    dataset_id: Optional[int],
) -> str:
    if dataset_id is None:
        return ""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    ds = result.scalar_one_or_none()
    if ds is None:
        return "\n（指定的数据集不存在或无权限访问。）"

    try:
        columns, rows = await run_in_threadpool(
            load_preview_records,
            ds.file_path,
            10,  # 只取 10 行预览样例
        )
    except Exception:
        return "\n（无法读取数据集预览文件。）"

    file_path = (Path(settings.UPLOAD_DIR) / ds.file_path).resolve()
    summaries = ""
    if file_path.suffix.lower() == ".csv":
        summaries = _build_column_summaries(file_path, columns)

    lines = [
        f"数据集「{ds.name}」，共 {ds.row_count} 行，{len(columns)} 列：{', '.join(columns)}",
    ]
    if summaries:
        lines.append("列统计：")
        lines.append(summaries)
    lines.append(f"预览 {len(rows)} 行：")
    for i, row in enumerate(rows, 1):
        lines.append(f"{i}. {row}")
    return "\n".join(lines)
