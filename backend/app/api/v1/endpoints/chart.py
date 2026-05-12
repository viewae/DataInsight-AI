from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Chart, User
from app.schemas.chart import ChartOut

router = APIRouter()


@router.get("/list", response_model=list[ChartOut])
async def list_charts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Chart)
        .where(Chart.user_id == user.id)
        .order_by(Chart.created_at.desc())
    )
    return [ChartOut.model_validate(c) for c in result.scalars().all()]


@router.get("/{chart_id}", response_model=ChartOut)
async def get_chart(
    chart_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chart = await db.get(Chart, chart_id)
    if chart is None or chart.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图表不存在")
    return ChartOut.model_validate(chart)


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chart(
    chart_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    chart = await db.get(Chart, chart_id)
    if chart is None or chart.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图表不存在")
    await db.delete(chart)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
