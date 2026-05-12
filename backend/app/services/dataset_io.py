import csv
import io
import json as json_mod
from pathlib import Path

import pandas as pd

from app.core.config import settings

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}


def safe_resolve(root: Path, user_path: str) -> Path:
    """安全拼接路径，防止路径穿越。"""
    if ".." in user_path.split("/") or ".." in user_path.split("\\"):
        raise PermissionError("invalid path")
    resolved = (root / user_path).resolve()
    if not str(resolved).startswith(str(root.resolve())):
        raise PermissionError("path traversal detected")
    return resolved

# 解析元数据时最多读取的行数（足够推断列类型）
META_PARSE_ROWS = 1000


def _read_meta(content: bytes, ext: str) -> tuple[int, list[dict[str, str]]]:
    """快速读取元数据：列信息 + 总行数，避免全量解析。"""
    ext = ext.lower()
    if ext == ".csv":
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        columns_meta = _infer_csv_dtypes(text)
        row_count = sum(1 for _ in reader)
        return row_count, columns_meta
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(io.BytesIO(content), nrows=META_PARSE_ROWS)
        row_count = len(pd.read_excel(io.BytesIO(content)))
        columns_meta = [{"name": str(c), "dtype": str(t)} for c, t in df.dtypes.items()]
        return row_count, columns_meta
    if ext == ".json":
        try:
            df = pd.read_json(io.BytesIO(content))
        except ValueError:
            df = pd.read_json(io.BytesIO(content), lines=True)
        row_count = len(df)
        columns_meta = [{"name": str(c), "dtype": str(t)} for c, t in df.dtypes.items()]
        return row_count, columns_meta
    raise ValueError(f"unsupported extension: {ext}")


def _infer_csv_dtypes(text: str) -> list[dict[str, str]]:
    """从 CSV 前 N 行推断列名和类型。"""
    head = io.StringIO("\n".join(text.split("\n")[: META_PARSE_ROWS + 1]))
    df = pd.read_csv(head)
    return [{"name": str(c), "dtype": str(t)} for c, t in df.dtypes.items()]


def read_full_dataframe(relative_path: str) -> pd.DataFrame:
    """Read full dataset from file path into DataFrame."""
    root = Path(settings.UPLOAD_DIR)
    path = safe_resolve(root, relative_path)
    if not path.is_file():
        raise FileNotFoundError("dataset file missing")

    ext = path.suffix.lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(path)
    elif ext == ".json":
        try:
            return pd.read_json(path)
        except ValueError:
            return pd.read_json(path, lines=True)
    else:
        raise ValueError("unsupported file")


def load_preview_records(relative_path: str, max_rows: int) -> tuple[list[str], list[dict]]:
    root = Path(settings.UPLOAD_DIR)
    path = safe_resolve(root, relative_path)
    if not path.is_file():
        raise FileNotFoundError("dataset file missing")

    ext = path.suffix.lower()
    if ext == ".csv":
        df = pd.read_csv(path, nrows=max_rows)
    elif ext in (".xlsx", ".xls"):
        df = pd.read_excel(path, nrows=max_rows)
    elif ext == ".json":
        try:
            df = pd.read_json(path)
        except ValueError:
            df = pd.read_json(path, lines=True)
        df = df.head(max_rows)
    else:
        raise ValueError("unsupported file")

    columns = [str(c) for c in df.columns]
    rows = df.fillna("").head(max_rows).to_dict(orient="records")
    return columns, rows
