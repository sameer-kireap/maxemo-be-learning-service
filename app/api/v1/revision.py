"""Revision recommendation engine API endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_attempt_service
from app.interface.attempt_service import IAttemptService
from app.schema.question import QuestionResponse
from app.schema.response import APIResponse

router = APIRouter(prefix="/revision", tags=["Revision Recommendation"])


@router.get(
    "/users/{user_id}",
    response_model=APIResponse[list[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get recommended weak questions for a learner to revise based on accuracy",
)
async def get_revision_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Max questions to recommend"),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[list[QuestionResponse]]:
    data = await service.get_revision_recommendations(user_id=user_id, limit=limit)
    return APIResponse(data=data, message="Revision recommendations retrieved successfully")
