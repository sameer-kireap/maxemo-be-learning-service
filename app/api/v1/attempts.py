"""Attempt and Analytics API endpoints."""

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_attempt_service
from app.interface.attempt_service import IAttemptService
from app.schema.attempt import (
    AttemptListFilterParams,
    AttemptResponse,
    AttemptSubmit,
    UserPerformanceResponse,
)
from app.schema.question import QuestionResponse
from app.schema.response import APIResponse, PaginatedResponse

router = APIRouter(prefix="/attempts", tags=["Attempts & Analytics"])


@router.post(
    "",
    response_model=APIResponse[AttemptResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record a learner question attempt (is_correct derived on server)",
)
async def submit_attempt(
    payload: AttemptSubmit,
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[AttemptResponse]:
    data = await service.submit_attempt(payload)
    return APIResponse(data=data, message="Attempt recorded successfully")


@router.get(
    "/users/{user_id}",
    response_model=APIResponse[PaginatedResponse[AttemptResponse]],
    status_code=status.HTTP_200_OK,
    summary="List a learner's attempts with pagination",
)
async def list_user_attempts(
    user_id: int,
    filter_params: AttemptListFilterParams = Depends(),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[PaginatedResponse[AttemptResponse]]:
    data = await service.list_user_attempts_paginated(user_id, filter_params)
    return APIResponse(data=data, message="User attempts retrieved successfully")


@router.get(
    "/users/{user_id}/performance",
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


@router.get(
    "/users/{user_id}/revision",
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
