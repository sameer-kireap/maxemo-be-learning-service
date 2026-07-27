"""Unit and integration tests for domain services."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.constant.difficulty import DifficultyLevel
from app.exception import (
    DuplicateException,
    InvalidOptionIndexException,
    NotFoundException,
)
from app.model.topic import Topic
from app.repository import (
    AttemptRepository,
    QuestionRepository,
    TopicRepository,
)
from app.service import AttemptService, QuestionService, TopicService


@pytest.mark.asyncio
async def test_topic_service_create_and_duplicate(db_session: AsyncSession) -> None:
    topic_repo = TopicRepository(db_session)
    topic_service = TopicService(topic_repo)

    topic = await topic_service.create_topic("Neuroology")
    assert topic.id is not None
    assert topic.name == "Neuroology"

    with pytest.raises(DuplicateException):
        await topic_service.create_topic("Neuroology")


@pytest.mark.asyncio
async def test_question_service_create_and_option_validation(
    db_session: AsyncSession,
) -> None:
    topic_repo = TopicRepository(db_session)
    q_repo = QuestionRepository(db_session)

    topic = await topic_repo.create(Topic(name="Biochemistry"))
    q_service = QuestionService(q_repo, topic_repo)

    # Valid question creation
    question = await q_service.create_question(
        text="What is ATP?",
        options=["Adenosine Triphosphate", "Amino Acid", "Protein", "Lipid"],
        correct_option_index=0,
        difficulty=DifficultyLevel.EASY,
        topic_ids=[topic.id],
    )
    assert question.id is not None
    assert question.correct_option_index == 0

    # Invalid option index out of range raises InvalidOptionIndexException
    with pytest.raises(InvalidOptionIndexException):
        await q_service.create_question(
            text="Invalid question?",
            options=["Option A", "Option B"],
            correct_option_index=5,
            difficulty=DifficultyLevel.HARD,
            topic_ids=[topic.id],
        )


@pytest.mark.asyncio
async def test_attempt_service_server_derived_correctness(
    db_session: AsyncSession,
) -> None:
    topic_repo = TopicRepository(db_session)
    q_repo = QuestionRepository(db_session)
    attempt_repo = AttemptRepository(db_session)

    q_service = QuestionService(q_repo, topic_repo)
    attempt_service = AttemptService(attempt_repo, q_repo)

    topic = await topic_repo.create(Topic(name="Anatomy"))
    question = await q_service.create_question(
        text="Which organ pumps blood?",
        options=["Brain", "Heart", "Liver", "Lungs"],
        correct_option_index=1,
        difficulty=DifficultyLevel.EASY,
        topic_ids=[topic.id],
    )

    user_id = 7771

    # Correct submission (selected index 1 == correct index 1)
    correct_attempt = await attempt_service.submit_attempt(
        user_id=user_id,
        question_id=question.id,
        selected_option_index=1,
        time_taken_seconds=10,
    )
    assert correct_attempt.is_correct is True

    # Incorrect submission (selected index 0 != correct index 1)
    incorrect_attempt = await attempt_service.submit_attempt(
        user_id=user_id,
        question_id=question.id,
        selected_option_index=0,
        time_taken_seconds=15,
    )
    assert incorrect_attempt.is_correct is False

    # Performance summary calculations in Service Layer
    summary = await attempt_service.get_user_performance_summary(user_id)
    assert summary["total_attempts"] == 2
    assert summary["correct_attempts"] == 1
    assert summary["accuracy_percentage"] == 50.0
    assert summary["avg_time_taken_seconds"] == 12.5


@pytest.mark.asyncio
async def test_attempt_service_invalid_option_index_raises(
    db_session: AsyncSession,
) -> None:
    topic_repo = TopicRepository(db_session)
    q_repo = QuestionRepository(db_session)
    attempt_repo = AttemptRepository(db_session)

    q_service = QuestionService(q_repo, topic_repo)
    attempt_service = AttemptService(attempt_repo, q_repo)

    topic = await topic_repo.create(Topic(name="Pathology"))
    question = await q_service.create_question(
        text="Sample question",
        options=["Option 1", "Option 2"],
        correct_option_index=0,
        difficulty=DifficultyLevel.EASY,
        topic_ids=[topic.id],
    )

    with pytest.raises(InvalidOptionIndexException):
        await attempt_service.submit_attempt(
            user_id=100,
            question_id=question.id,
            selected_option_index=99,
            time_taken_seconds=5,
        )


@pytest.mark.asyncio
async def test_service_not_found_raises(db_session: AsyncSession) -> None:
    topic_repo = TopicRepository(db_session)
    topic_service = TopicService(topic_repo)

    with pytest.raises(NotFoundException):
        await topic_service.get_topic_by_id(Topic(name="dummy").id)
