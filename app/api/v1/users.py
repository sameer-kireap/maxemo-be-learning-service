"""User Analytics & Revision API endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_attempt_service
from app.interface.attempt_service import IAttemptService
from app.schema.attempt import (
    AttemptListFilterParams,
    AttemptResponse,
    TopicRevisionResponse,
    UserPerformanceResponse,
)
from app.schema.question import QuestionResponse
from app.schema.response import APIResponse, PaginatedResponse

router = APIRouter(prefix="/users", tags=["User Analytics & Revision"])


@router.get(
    "/{user_id}/performance",
    response_model=APIResponse[UserPerformanceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get learner overall performance summary and topic-wise breakdown",
)
async def get_user_performance(
    user_id: int,
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[UserPerformanceResponse]:
    data = await service.get_user_performance_summary(user_id)
    return APIResponse(data=data, message="User performance calculated successfully")


@router.get(
    "/{user_id}/revision",
    response_model=APIResponse[TopicRevisionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get personalized topic revision queue (recommended top ~5 topics to revise next)",
)
async def get_topic_revision_recommendations(
    user_id: int,
    limit: int = Query(default=5, ge=1, le=20, description="Max topics to recommend"),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[TopicRevisionResponse]:
    data = await service.get_topic_revision_recommendations(user_id=user_id, limit=limit)
    return APIResponse(data=data, message="Topic revision queue calculated successfully")


@router.get(
    "/{user_id}/revision/questions",
    response_model=APIResponse[list[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get recommended weak questions for a learner to revise based on accuracy",
)
async def get_question_revision_recommendations(
    user_id: int,
    limit: int = Query(default=10, ge=1, le=50, description="Max questions to recommend"),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[list[QuestionResponse]]:
    data = await service.get_question_revision_recommendations(user_id=user_id, limit=limit)
    return APIResponse(data=data, message="Question revision recommendations retrieved")


@router.get(
    "/{user_id}/attempts",
    response_model=APIResponse[PaginatedResponse[AttemptResponse]],
    status_code=status.HTTP_200_OK,
    summary="List a learner's attempts history with pagination",
)
async def list_user_attempts(
    user_id: int,
    filter_params: AttemptListFilterParams = Depends(),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[PaginatedResponse[AttemptResponse]]:
    data = await service.list_user_attempts_paginated(user_id, filter_params)
    return APIResponse(data=data, message="User attempts retrieved successfully")
