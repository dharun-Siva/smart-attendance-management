from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.attendance import router as attendance_router
from app.api.v1.corrections import router as corrections_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(admin_router, tags=["admin"])
api_router.include_router(attendance_router, tags=["attendance"])
api_router.include_router(corrections_router, tags=["corrections"])
api_router.include_router(reports_router, tags=["reports"])
