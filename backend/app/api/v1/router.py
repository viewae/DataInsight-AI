from fastapi import APIRouter

from app.api.v1.endpoints import ai, auth, chart, data, dataset, project, report, session

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dataset.router, prefix="/dataset", tags=["dataset"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(chart.router, prefix="/chart", tags=["chart"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
