import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from openai import APIConnectionError, APIStatusError, AuthenticationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import AnalysisSession, Chart, Dataset, User
from app.schemas.chart import ChartOut
from app.schemas.session import (
    SessionCreate,
    SessionOut,
    SessionQueryRequest,
    SessionQueryResponse,
)
from app.services import llm
from app.services.dataset_context import build_dataset_context

router = APIRouter()


def _try_parse_json(raw: str) -> object:
    """Best-effort JSON extraction from LLM response (handles markdown fence)."""
    if raw.startswith("{"):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    if "```json" in raw:
        try:
            block = raw.split("```json")[1].split("```")[0].strip()
            return json.loads(block)
        except (IndexError, json.JSONDecodeError):
            pass
    if "```" in raw:
        try:
            block = raw.split("```")[1].split("```")[0].strip()
            return json.loads(block)
        except (IndexError, json.JSONDecodeError):
            pass
    return None


def _normalize_chart_data(data: object) -> list[dict]:
    """将 LLM 返回的各种 data 格式统一为 [{name, value}, ...]"""
    if not isinstance(data, list):
        if isinstance(data, dict):
            # {A: 10, B: 20} -> [{name: A, value: 10}, ...]
            return [{"name": str(k), "value": v if isinstance(v, (int, float)) else 0} for k, v in data.items()]
        return []
    if not data:
        return []
    # 如果每项是 [cat, val] 格式
    if isinstance(data[0], (list, tuple)):
        return [{"name": str(item[0]), "value": float(item[1]) if len(item) > 1 else 0} for item in data]
    # 如果每项已经是 {name, value} 或类似 dict
    if isinstance(data[0], dict):
        out = []
        for d in data:
            keys = list(d.keys())
            name = str(d.get("name") or d.get(keys[0], ""))
            raw_val = d.get("value") or d.get(keys[1]) if len(keys) > 1 else 0
            try:
                value = float(raw_val)
            except (TypeError, ValueError):
                value = 0
            out.append({"name": name, "value": value})
        return out
    return []


def _normalize_scatter_data(data: object) -> list[dict]:
    """散点图保留原始数值 x/y，不转成 name/value。"""
    if not isinstance(data, list) or not data:
        return []
    if isinstance(data[0], dict):
        has_xy = "x" in data[0] and "y" in data[0]
        out = []
        for i, d in enumerate(data):
            name = str(d.get("name", d.get(list(d.keys())[0], "")))
            if has_xy:
                try:
                    out.append({"x": float(d["x"]), "y": float(d["y"]), "name": name})
                except (TypeError, ValueError):
                    out.append({"x": 0, "y": 0, "name": name})
            else:
                # name/value 格式兜底：用序号作 x
                val = d.get("value", 0)
                try:
                    out.append({"x": float(i), "y": float(val), "name": name})
                except (TypeError, ValueError):
                    out.append({"x": float(i), "y": 0, "name": name})
        return out
    if isinstance(data[0], (list, tuple)):
        return [{"x": float(d[0]), "y": float(d[1]), "name": ""} for d in data if len(d) >= 2]
    return []


def _assert_chart_suggestions(raw: object) -> Optional[list]:
    """Parse chart suggestions from LLM output; return None on failure."""
    if not isinstance(raw, list):
        return None
    out = []
    for item in raw:
        if isinstance(item, dict) and "chart_type" in item:
            if item.get("chart_type") == "scatter":
                item["data"] = _normalize_scatter_data(item.get("data"))
            else:
                item["data"] = _normalize_chart_data(item.get("data"))
                item.pop("x_axis", None)
                item.pop("y_axis", None)
            out.append(item)
    return out or None


@router.post("/create", response_model=SessionOut)
async def create_session(
    body: SessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ds = await db.get(Dataset, body.dataset_id)
    if ds is None or ds.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="数据集不存在")

    session = AnalysisSession(
        user_id=user.id,
        dataset_id=body.dataset_id,
        title=body.title or ds.name,
        conversation_history=[],
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return SessionOut.model_validate(session)


@router.get("/list", response_model=list[SessionOut])
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AnalysisSession)
        .where(AnalysisSession.user_id == user.id)
        .order_by(AnalysisSession.created_at.desc())
    )
    return [SessionOut.model_validate(s) for s in result.scalars().all()]


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(AnalysisSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    return SessionOut.model_validate(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(AnalysisSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    await db.delete(session)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{session_id}/query", response_model=SessionQueryResponse)
async def query_session(
    session_id: int,
    body: SessionQueryRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await db.get(AnalysisSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # build context from the session's dataset
    ctx = await build_dataset_context(db, user.id, session.dataset_id)

    system = (
        "你是 DataInsight AI 的数据分析助手，用简洁中文回答。\n"
        "结合下方数据集摘要（若有）理解用户问题；无法从数据中得出结论时要说明。\n\n"
        "你可以提供图表建议来辅助回答。如果问题适合可视化，请在回答的 JSON 中加入 "
        '"chart_suggestions" 数组，每项包含：\n'
        '- chart_type: bar（柱状图-对比分类） / line（折线图-趋势） / pie（饼图-占比） / scatter（散点图-相关性）\n'
        '- title: 图表标题\n'
        '- 非散点图: data 为 {name: 分类名, value: 数值}，如 [{"name":"A","value":10}]\n'
        '- 散点图: data 为 {name: 标签, x: 数值, y: 数值}，如 [{"name":"电影A","x":8.5,"y":1200}]\n'
        '从数据不同维度生成 4 个图表，四种类型各一个（bar/line/pie/scatter 各一），不要重复类型。\n'
        '返回格式必须是 JSON，包含 "answer" 和可选的 "chart_suggestions" 字段。'
    )

    # build message list: system + recent history + new question
    history = session.conversation_history or []
    recent = history[-40:]  # up to 20 turns (user+assistant pairs)

    messages = [{"role": "system", "content": system}]
    for msg in recent:
        messages.append({"role": msg["role"], "content": msg["content"]})

    user_content = body.question.strip()
    if ctx:
        user_content = f"{user_content}\n\n---\n数据集上下文：\n{ctx}"
    messages.append({"role": "user", "content": user_content})

    try:
        raw = await llm.chat(messages)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="未配置 LLM：在环境变量中设置 LLM_API_KEY / DEEPSEEK_API_KEY / OPENAI_API_KEY 之一",
        ) from None
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"LLM 鉴权失败：{e!s}",
        ) from e
    except APIStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM 接口错误：{e!s}",
        ) from e
    except APIConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"无法连接 LLM 服务：{e!s}",
        ) from e

    # try to parse structured JSON from LLM response
    answer = raw
    chart_suggestions = None
    parsed = _try_parse_json(raw)
    if isinstance(parsed, dict):
        answer = parsed.get("answer", raw)
        chart_suggestions = _assert_chart_suggestions(parsed.get("chart_suggestions"))

    # save conversation history
    history.append({"role": "user", "content": body.question.strip()})
    history.append({"role": "assistant", "content": answer})
    session.conversation_history = history

    # save chart suggestions
    if chart_suggestions:
        for sug in chart_suggestions:
            chart = Chart(
                user_id=user.id,
                session_id=session.id,
                chart_type=sug.get("chart_type", "bar"),
                config=sug,
            )
            db.add(chart)

    await db.commit()

    return SessionQueryResponse(
        answer=answer,
        model=settings.LLM_MODEL,
        chart_suggestions=chart_suggestions,
    )
