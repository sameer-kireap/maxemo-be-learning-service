"""Database script to generate user question attempts on demand."""

import argparse
import asyncio
import logging
import random

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session_factory
from app.core.logger import setup_logging
from app.model.attempt import QuestionAttempt
from app.model.question import Question

logger = logging.getLogger(__name__)


async def seed_user_attempts(
    session: AsyncSession,
    user_ids: list[int],
    attempts_per_user: int | None = None,
) -> None:
    """Generates random realistic attempts for questions in the database."""
    # Fetch existing questions
    stmt = select(Question)
    questions = list((await session.execute(stmt)).scalars().all())

    if not questions:
        logger.warning(
            "No questions found in database! Please run `uv run python -m scripts.seed_db` first."
        )
        return

    total_created = 0
    for uid in user_ids:
        logger.info("Generating attempts for user_id=%s...", uid)
        target_questions = (
            questions[:attempts_per_user]
            if attempts_per_user is not None
            else questions
        )

        for q in target_questions:
            # Simulate performance curve
            accuracy = 0.80 if uid % 2 == 0 else 0.55
            is_correct_choice = random.random() < accuracy

            if is_correct_choice:
                selected_idx = q.correct_option_index
            else:
                wrong_indices = [
                    i for i in range(len(q.options)) if i != q.correct_option_index
                ]
                selected_idx = random.choice(wrong_indices) if wrong_indices else 0

            attempt = QuestionAttempt(
                user_id=uid,
                question_id=q.id,
                selected_option_index=selected_idx,
                is_correct=(selected_idx == q.correct_option_index),
                time_taken_seconds=random.randint(10, 50),
            )
            session.add(attempt)
            total_created += 1

    await session.commit()
    logger.info("Successfully generated %d attempts for users %s!", total_created, user_ids)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate mock question attempts for users.")
    parser.add_argument(
        "--user-id",
        type=int,
        nargs="+",
        default=[101, 102, 103],
        help="List of user IDs to generate attempts for (default: 101 102 103)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Max attempts per user (default: all questions)",
    )
    args = parser.parse_args()

    settings = get_settings()
    setup_logging(settings.log_level)
    session_factory = get_session_factory()

    async with session_factory() as session:
        await seed_user_attempts(
            session=session,
            user_ids=args.user_id,
            attempts_per_user=args.count,
        )


if __name__ == "__main__":
    asyncio.run(main())
