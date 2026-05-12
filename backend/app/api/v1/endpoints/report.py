from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import AnalysisSession, Chart, Report, User
from app.schemas.report import ReportCreate, ReportOut

router = APIRouter()


def _build_html_report(session: AnalysisSession, charts: list[Chart]) -> str:
    """Compile session Q&A and charts into an HTML report."""
    parts = [
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>",
        "<title>数据分析报告</title>",
        "<style>body{font-family:sans-serif;max-width:800px;margin:0 auto;padding:20px}",
        ".qa{margin:16px 0;padding:12px;border-left:3px solid #409eff;background:#f5f7fa}",
        ".qa-user{font-weight:600;color:#303133}.qa-ai{color:#606266;margin-top:4px}</style></head><body>",
        f"<h1>数据分析报告</h1>",
        f"<p>生成时间：{session.created_at.strftime('%Y-%m-%d %H:%M')}</p>",
        f"<p>数据集 ID：{session.dataset_id}</p>",
        "<hr>",
    ]
    history = session.conversation_history or []
    for i in range(0, len(history), 2):
        user_msg = history[i] if i < len(history) else None
        ai_msg = history[i + 1] if i + 1 < len(history) else None
        if user_msg:
            parts.append(f"<div class='qa'><div class='qa-user'>问：{user_msg['content']}</div>")
        if ai_msg:
            parts.append(f"<div class='qa-ai'>答：{ai_msg['content']}</div></div>")

    if charts:
        parts.append("<h2>图表</h2>")
        for c in charts:
            parts.append(
                f"<div style='margin:12px 0'><h3>{c.config.get('title', c.chart_type)}</h3>"
                f"<p>类型：{c.chart_type}</p>"
                f"<pre>{str(c.config)[:500]}</pre></div>"
            )

    parts.append("</body></html>")
    return "\n".join(parts)


@router.post("/generate", response_model=ReportOut)
async def generate(
    body: ReportCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.quota_used >= user.quota_limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="本月 AI 调用次数已达上限",
        )

    session = await db.get(AnalysisSession, body.session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    result = await db.execute(
        select(Chart).where(Chart.session_id == session.id, Chart.user_id == user.id)
    )
    charts = list(result.scalars().all())

    title = body.title or f"报告-会话#{session.id}"
    content = _build_html_report(session, charts)

    report = Report(user_id=user.id, title=title, content=content)
    db.add(report)
    user.quota_used += 1
    await db.commit()
    await db.refresh(report)
    return ReportOut.model_validate(report)


@router.get("/list", response_model=list[ReportOut])
async def list_reports(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Report)
        .where(Report.user_id == user.id)
        .order_by(Report.created_at.desc())
    )
    return [ReportOut.model_validate(r) for r in result.scalars().all()]


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await db.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    return ReportOut.model_validate(report)


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await db.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    return Response(
        content=report.content or "",
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="report_{report_id}.html"'},
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await db.get(Report, report_id)
    if report is None or report.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")
    await db.delete(report)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
