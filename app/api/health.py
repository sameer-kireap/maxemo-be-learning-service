"""Health check API endpoint."""

from fastapi import APIRouter, Depends, status

from app.core.config import Settings, get_settings
from app.schema.health import HealthResponse
from app.schema.response import APIResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=APIResponse[HealthResponse],
    status_code=status.HTTP_200_OK,
    summary="Service health check",
)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> APIResponse[HealthResponse]:
    payload = HealthResponse(
        status="healthy",
        service=settings.app_name,
        version=settings.app_version,
    )
    return APIResponse(data=payload, message="Service is operational")
