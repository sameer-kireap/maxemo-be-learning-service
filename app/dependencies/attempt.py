"""Attempt dependency injection factory functions."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db_session
from app.dependencies.question import get_question_repository
from app.interface.attempt_service import IAttemptService
from app.repository.attempt_repository import AttemptRepository
from app.repository.question_repository import QuestionRepository
from app.service.attempt_service import AttemptService


def get_attempt_repository(session: AsyncSession = Depends(get_db_session)) -> AttemptRepository:
    return AttemptRepository(session)


def get_attempt_service(
    a_repo: AttemptRepository = Depends(get_attempt_repository),
    q_repo: QuestionRepository = Depends(get_question_repository),
) -> IAttemptService:
    return AttemptService(a_repo, q_repo)
