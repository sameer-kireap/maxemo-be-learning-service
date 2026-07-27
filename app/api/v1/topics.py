"""Topic API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status

from app.dependencies import get_topic_service
from app.interface.topic_service import ITopicService
from app.schema.filter import FilterParams
from app.schema.response import APIResponse, PaginatedResponse
from app.schema.topic import TopicCreate, TopicResponse

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.post(
    "",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new learning topic",
)
async def create_topic(
    payload: TopicCreate,
    service: ITopicService = Depends(get_topic_service),
) -> APIResponse[TopicResponse]:
    data = await service.create_topic(payload)
    return APIResponse(data=data, message="Topic created successfully")


@router.get(
    "",
    response_model=APIResponse[PaginatedResponse[TopicResponse]],
    status_code=status.HTTP_200_OK,
    summary="List all learning topics with search, sorting, and pagination",
)
async def list_topics(
    filter_params: FilterParams = Depends(),
    service: ITopicService = Depends(get_topic_service),
) -> APIResponse[PaginatedResponse[TopicResponse]]:
    data = await service.list_topics_paginated(filter_params)
    return APIResponse(data=data, message="Topics retrieved successfully")


@router.get(
    "/{topic_id}",
    response_model=APIResponse[TopicResponse],
    status_code=status.HTTP_200_OK,
    summary="Get a single topic by UUID",
)
async def get_topic_by_id(
    topic_id: uuid.UUID,
    service: ITopicService = Depends(get_topic_service),
) -> APIResponse[TopicResponse]:
    data = await service.get_topic_by_id(topic_id)
    return APIResponse(data=data, message="Topic retrieved successfully")
