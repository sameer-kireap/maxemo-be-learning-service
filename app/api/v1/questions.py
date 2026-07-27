"""Question API endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_question_service
from app.interface.question_service import IQuestionService
from app.schema.question import (
    QuestionAdminResponse,
    QuestionCreate,
    QuestionListFilterParams,
    QuestionResponse,
    QuestionUpdate,
)
from app.schema.response import APIResponse, PaginatedResponse

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post(
    "",
    response_model=APIResponse[QuestionAdminResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new question",
)
async def create_question(
    payload: QuestionCreate,
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[QuestionAdminResponse]:
    data = await service.create_question(payload)
    return APIResponse(data=data, message="Question created successfully")


@router.get(
    "/practice",
    response_model=APIResponse[list[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get random practice questions for selected topics",
)
async def get_practice_questions(
    topic_ids: list[uuid.UUID] = Query(..., description="Topic UUIDs to practice"),
    limit: int = Query(default=10, ge=1, le=50, description="Max questions"),
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[list[QuestionResponse]]:
    data = await service.get_practice_questions(topic_ids=topic_ids, limit=limit)
    return APIResponse(data=data, message="Practice questions retrieved successfully")


@router.get(
    "",
    response_model=APIResponse[PaginatedResponse[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="List questions with optional topic and difficulty filters",
)
async def list_questions(
    filter_params: QuestionListFilterParams = Depends(),
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[PaginatedResponse[QuestionResponse]]:
    data = await service.list_questions_paginated(
        filter_params=filter_params,
        topic_id=filter_params.topic_id,
        difficulty=filter_params.difficulty,
    )
    return APIResponse(data=data, message="Questions retrieved successfully")


@router.get(
    "/{question_id}",
    response_model=APIResponse[QuestionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get question by ID (learner view — excludes correct_option_index)",
)
async def get_question_by_id(
    question_id: uuid.UUID,
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[QuestionResponse]:
    data = await service.get_question_by_id(question_id)
    return APIResponse(data=data, message="Question retrieved successfully")


@router.put(
    "/{question_id}",
    response_model=APIResponse[QuestionAdminResponse],
    status_code=status.HTTP_200_OK,
    summary="Update a question",
)
async def update_question(
    question_id: uuid.UUID,
    payload: QuestionUpdate,
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[QuestionAdminResponse]:
    data = await service.update_question(question_id=question_id, payload=payload)
    return APIResponse(data=data, message="Question updated successfully")


@router.delete(
    "/{question_id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
    summary="Delete a question",
)
async def delete_question(
    question_id: uuid.UUID,
    service: IQuestionService = Depends(get_question_service),
) -> APIResponse[None]:
    await service.delete_question(question_id)
    return APIResponse(data=None, message="Question deleted successfully")
