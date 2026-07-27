"""Question dependency injection factory functions."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.dependencies.topic import get_topic_repository
from app.interface.question_service import IQuestionService
from app.repository.question_repository import QuestionRepository
from app.repository.topic_repository import TopicRepository
from app.service.question_service import QuestionService


def get_question_repository(session: AsyncSession = Depends(get_db_session)) -> QuestionRepository:
    return QuestionRepository(session)


def get_question_service(
    q_repo: QuestionRepository = Depends(get_question_repository),
    t_repo: TopicRepository = Depends(get_topic_repository),
) -> IQuestionService:
    return QuestionService(q_repo, t_repo)
