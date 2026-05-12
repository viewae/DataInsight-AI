import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from openai import APIConnectionError, APIStatusError, AuthenticationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Dataset, User
from app.schemas.ai import (
    AIQueryRequest,
    AIQueryResponse,
    AutoEDARequest,
    AutoEDAResponse,
    DetectAnomalyRequest,
    DetectAnomalyResponse,
    ForecastRequest,
    ForecastResponse,
    SuggestChartRequest,
    SuggestChartResponse,
)
from app.services import llm
from app.services.dataset_context import build_dataset_context
from app.services.dataset_io import load_preview_records

router = APIRouter()

_LLM_ERROR_MAP: dict[type, tuple[int, str]] = {
    ValueError: (status.HTTP_503_SERVICE_UNAVAILABLE, "未配置 LLM API 密钥"),
    AuthenticationError: (status.HTTP_401_UNAUTHORIZED, "LLM 鉴权失败"),
    APIStatusError: (status.HTTP_502_BAD_GATEWAY, "LLM 接口错误"),
    APIConnectionError: (status.HTTP_503_SERVICE_UNAVAILABLE, "无法连接 LLM 服务"),
}


def _check_quota(user: User) -> None:
    if user.quota_used >= user.quota_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="本月 AI 调用次数已达上限")


def _llm_error(e: Exception) -> None:
    for exc_type, (code, msg) in _LLM_ERROR_MAP.items():
        if isinstance(e, exc_type):
            raise HTTPException(status_code=code, detail=f"{msg}：{e!s}") from e
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


def _increment_quota(user: User, db: AsyncSession) -> None:
    user.quota_used += 1


async def _load_data(
    db: AsyncSession, user_id: int, dataset_id: int
) -> tuple[Dataset, list[str], list[dict[str, Any]]]:
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.user_id == user_id)
    )
    ds = result.scalar_one_or_none()
    if ds is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据集不存在")
    columns, rows = load_preview_records(ds.file_path, settings.PREVIEW_MAX_ROWS)
    return ds, columns, rows


def _json_parse(raw: str) -> dict[str, Any]:
    """Best-effort JSON extraction from LLM response."""
    if raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    # try to find JSON block in markdown
    if "```json" in raw:
        try:
            block = raw.split("```json")[1].split("```")[0].strip()
            return json.loads(block)
        except (IndexError, json.JSONDecodeError):
            pass
    return {}


@router.post("/query", response_model=AIQueryResponse)
async def query(
    body: AIQueryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ctx = await build_dataset_context(db, user.id, body.dataset_id)
    system = (
        "你是 DataInsight AI 的数据分析助手，用简洁中文回答。"
        "结合下方数据集摘要（若有）理解用户问题；无法从数据中得出结论时要说明。"
    )
    user_content = body.question.strip()
    if ctx:
        user_content = f"{user_content}\n\n---\n数据集上下文：\n{ctx}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
    try:
        answer = await llm.chat(messages)
    except Exception as e:
        _llm_error(e)

    await db.commit()
    return AIQueryResponse(answer=answer, model=settings.LLM_MODEL)


@router.post("/auto-eda", response_model=AutoEDAResponse)
async def auto_eda(
    body: AutoEDARequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds, columns, rows = await _load_data(db, user.id, body.dataset_id)

    preview = json.dumps(rows[:20], ensure_ascii=False)
    system = (
        "你是数据分析专家。分析以下数据集预览，返回 JSON，包含：\n"
        '1. "summary": 数据概况的中文描述\n'
        '2. "column_stats": 每列的统计信息，含 name、dtype、missing、unique\n'
        '3. "correlations": 数值列的相关系数（若有）\n'
        '4. "warnings": 数据质量问题列表\n'
        "只返回 JSON，不要其他文字。"
    )
    prompt = (
        f"数据集「{ds.name}」，共 {ds.row_count} 行。\n"
        f"列：{', '.join(columns)}\n预览数据：\n{preview}"
    )

    try:
        raw = await llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.1,
        )
    except Exception as e:
        _llm_error(e)

    parsed = _json_parse(raw)
    await db.commit()

    # 兼容 LLM 返回 dict 而非 list 的情况
    corr = parsed.get("correlations", [])
    if isinstance(corr, dict):
        if all(isinstance(v, dict) for v in corr.values()):
            corr = list(corr.values())
        else:
            corr = []

    return AutoEDAResponse(
        summary=parsed.get("summary", raw[:200]),
        column_stats=parsed.get("column_stats", []),
        correlations=corr,
        warnings=parsed.get("warnings", []),
    )


@router.post("/suggest-chart", response_model=SuggestChartResponse)
async def suggest_chart(
    body: SuggestChartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds, columns, _rows = await _load_data(db, user.id, body.dataset_id)

    meta = json.dumps(ds.columns_meta, ensure_ascii=False)
    prompt_text = (
        f"数据集「{ds.name}」的列定义：{meta}\n"
        f"问：{body.question or '推荐合适的可视化图表'}\n"
    )

    system = (
        "根据数据列定义和业务问题，推荐最合适的图表类型。返回 JSON 格式的 suggestions 数组，"
        "每项包含 chart_type（bar/line/pie/scatter/histogram）、title、x_axis、y_axis、aggregation。"
        "只返回 JSON，不要其他文字。"
    )

    try:
        raw = await llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt_text}],
            temperature=0.1,
        )
    except Exception as e:
        _llm_error(e)

    parsed = _json_parse(raw)
    await db.commit()

    return SuggestChartResponse(suggestions=parsed.get("suggestions", []))


@router.post("/detect-anomaly", response_model=DetectAnomalyResponse)
async def detect_anomaly(
    body: DetectAnomalyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _ds, _columns, rows = await _load_data(db, user.id, body.dataset_id)

    # use IQR for numerical detection
    values = []
    for r in rows:
        v = r.get(body.column)
        if v is not None:
            try:
                values.append(float(v))
            except (ValueError, TypeError):
                pass

    anomalies: list[dict[str, Any]] = []
    if len(values) > 4:
        sorted_v = sorted(values)
        q1 = sorted_v[len(sorted_v) // 4]
        q3 = sorted_v[(3 * len(sorted_v)) // 4]
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        for r in rows:
            v = r.get(body.column)
            if v is not None:
                try:
                    fv = float(v)
                    if fv < lower or fv > upper:
                        anomalies.append(
                            {"index": rows.index(r), "value": fv, "reason": "超出 IQR 范围"}
                        )
                except (ValueError, TypeError):
                    pass

    summary = f"列「{body.column}」：{len(values)} 个数值，检出 {len(anomalies)} 个异常值（IQR 方法）"
    await db.commit()

    return DetectAnomalyResponse(column=body.column, anomalies=anomalies[:50], summary=summary)


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(
    body: ForecastRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _ds, columns, rows = await _load_data(db, user.id, body.dataset_id)

    if body.date_column not in columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据集中不存在日期列「{body.date_column}」",
        )
    if body.value_column not in columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"数据集中不存在数值列「{body.value_column}」",
        )

    data_sample = json.dumps(rows[-30:], ensure_ascii=False)
    system = (
        "你是时间序列预测专家。根据以下数据样本，预测未来趋势。"
        "返回 JSON，包含 forecast 数组，每项含 date（或序号）和 value。"
        "只返回 JSON，不要其他文字。"
    )
    prompt = (
        f"数据集含列 {', '.join(columns)}。\n"
        f"日期列：{body.date_column}，数值列：{body.value_column}。\n"
        f"最近数据样本：\n{data_sample}\n"
        f"请预测未来 {body.periods} 个时间点的值。"
    )

    try:
        raw = await llm.chat(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.1,
        )
    except Exception as e:
        _llm_error(e)

    parsed = _json_parse(raw)
    await db.commit()

    return ForecastResponse(
        forecast=parsed.get("forecast", []),
        model=settings.LLM_MODEL,
    )
