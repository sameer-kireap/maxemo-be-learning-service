"""API v1 router assembly."""

from fastapi import APIRouter

from app.api.v1.attempts import router as attempts_router
from app.api.v1.questions import router as questions_router
from app.api.v1.topics import router as topics_router
from app.api.v1.users import router as users_router

api_router = APIRouter()

api_router.include_router(topics_router)
api_router.include_router(questions_router)
api_router.include_router(attempts_router)
api_router.include_router(users_router)

__all__ = ["api_router"]
