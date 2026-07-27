"""Attempt API endpoints."""

from fastapi import APIRouter, Depends, status

from app.dependencies import get_attempt_service
from app.interface.attempt_service import IAttemptService
from app.schema.attempt import AttemptResponse, AttemptSubmit
from app.schema.filter import FilterParams
from app.schema.response import APIResponse, PaginatedResponse

router = APIRouter(prefix="/attempts", tags=["Attempts"])


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
    filter_params: FilterParams = Depends(),
    service: IAttemptService = Depends(get_attempt_service),
) -> APIResponse[PaginatedResponse[AttemptResponse]]:
    data = await service.list_user_attempts_paginated(user_id, filter_params)
    return APIResponse(data=data, message="User attempts retrieved successfully")
