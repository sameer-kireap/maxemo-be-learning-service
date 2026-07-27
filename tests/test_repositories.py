"""Integration tests for repositories."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.constant.difficulty import DifficultyLevel
from app.model.attempt import QuestionAttempt
from app.model.question import Question
from app.model.topic import Topic
from app.repository import (
    AttemptRepository,
    QuestionRepository,
    TopicRepository,
)
from app.schema.filter import FilterParams


@pytest.mark.asyncio
async def test_topic_repository_crud(db_session: AsyncSession) -> None:
    repo = TopicRepository(db_session)

    # Create topic
    topic = Topic(name="Cardiology Basics")
    created = await repo.create(topic)
    assert created.id is not None
    assert created.name == "Cardiology Basics"

    # Get by id
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Cardiology Basics"

    # Get by name
    by_name = await repo.get_by_name("Cardiology Basics")
    assert by_name is not None
    assert by_name.id == created.id

    # List all via list_generic
    items, total = await repo.list_topics(FilterParams(offset=0, limit=10))
    assert total >= 1
    assert any(t.id == created.id for t in items)


@pytest.mark.asyncio
async def test_question_repository_crud(db_session: AsyncSession) -> None:
    topic_repo = TopicRepository(db_session)
    question_repo = QuestionRepository(db_session)

    topic = await topic_repo.create(Topic(name="Pharmacology"))

    question = Question(
        text="Which drug is a beta-blocker?",
        options=["Metoprolol", "Amlodipine", "Furosemide", "Atorvastatin"],
        correct_option_index=0,
        difficulty=DifficultyLevel.EASY,
        topics=[topic],
    )

    created_q = await question_repo.create(question)
    assert created_q.id is not None
    assert created_q.text == "Which drug is a beta-blocker?"

    fetched_q = await question_repo.get_by_id(created_q.id)
    assert fetched_q is not None
    assert len(fetched_q.topics) == 1
    assert fetched_q.topics[0].name == "Pharmacology"

    # Filter by topic via list_questions
    items, total = await question_repo.list_questions(
        FilterParams(offset=0, limit=10), topic_id=topic.id
    )
    assert total >= 1
    assert any(q.id == created_q.id for q in items)

    # Delete question
    deleted = await question_repo.delete(created_q.id)
    assert deleted is True
    assert await question_repo.get_by_id(created_q.id) is None


@pytest.mark.asyncio
async def test_attempt_repository_raw_queries(db_session: AsyncSession) -> None:
    q_repo = QuestionRepository(db_session)
    attempt_repo = AttemptRepository(db_session)

    question = await q_repo.create(
        Question(
            text="What is the unit of force?",
            options=["Newton", "Joule", "Watt", "Pascal"],
            correct_option_index=0,
            difficulty=DifficultyLevel.EASY,
        )
    )

    user_id = 99991

    # Add 2 attempts: 1 correct, 1 incorrect
    await attempt_repo.create(
        QuestionAttempt(
            user_id=user_id,
            question_id=question.id,
            selected_option_index=0,
            is_correct=True,
            time_taken_seconds=15,
        )
    )
    await attempt_repo.create(
        QuestionAttempt(
            user_id=user_id,
            question_id=question.id,
            selected_option_index=1,
            is_correct=False,
            time_taken_seconds=25,
        )
    )

    # Verify raw summary tuple: row containing (total, correct, total_time)
    row = await attempt_repo.get_raw_user_performance(user_id)
    assert row.total_attempts == 2
    assert row.correct_attempts == 1
    assert float(row.total_time_seconds) == 40.0

    # Verify incorrect attempts
    incorrect = await attempt_repo.get_incorrect_attempts_by_user(user_id)
    assert len(incorrect) == 1
    assert incorrect[0].is_correct is False
    assert incorrect[0].selected_option_index == 1
