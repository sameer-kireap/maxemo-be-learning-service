"""Topic dependency injection factory functions."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.interface.topic_service import ITopicService
from app.repository.topic_repository import TopicRepository
from app.service.topic_service import TopicService


def get_topic_repository(session: AsyncSession = Depends(get_db_session)) -> TopicRepository:
    return TopicRepository(session)


def get_topic_service(
    repo: TopicRepository = Depends(get_topic_repository),
) -> ITopicService:
    return TopicService(repo)
