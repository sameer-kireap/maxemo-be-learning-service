"""API v1 router assembly."""

from fastapi import APIRouter

from app.api.v1.attempts import router as attempts_router
from app.api.v1.health import router as health_router
from app.api.v1.performance import router as performance_router
from app.api.v1.questions import router as questions_router
from app.api.v1.revision import router as revision_router
from app.api.v1.topics import router as topics_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(topics_router)
api_router.include_router(questions_router)
api_router.include_router(attempts_router)
api_router.include_router(performance_router)
api_router.include_router(revision_router)

__all__ = ["api_router"]
