"""API router — aggregates all feature routers."""

from fastapi import APIRouter

from app.api.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)

# Feature routers are added here as phases progress:
# api_router.include_router(topics_router)
# api_router.include_router(questions_router)
# api_router.include_router(attempts_router)
# api_router.include_router(performance_router)
# api_router.include_router(revision_router)
