"""Performance analytics API endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_attempt_service
from app.interface.attempt_service import IAttemptService
from app.schema.attempt import UserPerformanceResponse
from app.schema.response import APIResponse

router = APIRouter(prefix="/performance", tags=["Performance Analytics"])


@router.get(
    "/users/{user_id}",
    response_model=APIResponse[UserPerformanceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user overall performance summary and topic-wise breakdown",
)
async def get_user_performance(
    user_id: int,
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[UserPerformanceResponse]:
    data = await service.get_user_performance_summary(user_id)
    return APIResponse(data=data, message="User performance calculated successfully")
