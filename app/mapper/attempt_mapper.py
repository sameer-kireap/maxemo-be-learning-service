"""Attempt DTO mapper for entity-to-schema conversions and performance math."""

from datetime import UTC, datetime
from typing import Any

from app.model.attempt import QuestionAttempt
from app.schema.attempt import (
    AttemptResponse,
    AttemptSubmit,
    TopicPerformanceResponse,
    TopicRevisionRecommendation,
    TopicRevisionResponse,
    UserPerformanceResponse,
)


class AttemptMapper:
    """Provides pure static transformation functions for QuestionAttempt entity & aggregates."""

    @staticmethod
    def to_entity(payload: AttemptSubmit, is_correct: bool) -> QuestionAttempt:
        return QuestionAttempt(
            user_id=payload.user_id,
            question_id=payload.question_id,
            selected_option_index=payload.selected_option_index,
            is_correct=is_correct,
            time_taken_seconds=payload.time_taken_seconds,
        )

    @staticmethod
    def to_response(attempt: QuestionAttempt) -> AttemptResponse:
        from app.mapper.question_mapper import QuestionMapper

        q_dto = QuestionMapper.to_response(attempt.question) if attempt.question else None

        return AttemptResponse(
            id=attempt.id,
            user_id=attempt.user_id,
            question_id=attempt.question_id,
            selected_option_index=attempt.selected_option_index,
            is_correct=attempt.is_correct,
            time_taken_seconds=attempt.time_taken_seconds,
            created_at=attempt.created_at,
            question=q_dto,
        )

    @staticmethod
    def to_response_list(attempts: list[QuestionAttempt]) -> list[AttemptResponse]:
        return [AttemptMapper.to_response(a) for a in attempts]

    @staticmethod
    def to_user_performance(
        user_id: int, user_row: Any, topic_rows: Any  # noqa: ANN401
    ) -> UserPerformanceResponse:
        total = user_row.total_attempts or 0
        correct = user_row.correct_attempts or 0
        total_time = user_row.total_time_seconds or 0

        accuracy = (correct / total * 100.0) if total > 0 else 0.0
        avg_time = (total_time / total) if total > 0 else 0.0

        topic_stats: list[TopicPerformanceResponse] = []
        for r in topic_rows:
            t_total = r.total_attempts or 0
            t_correct = r.correct_attempts or 0
            t_acc = (t_correct / t_total * 100.0) if t_total > 0 else 0.0
            topic_stats.append(
                TopicPerformanceResponse(
                    topic_id=r.topic_id,
                    topic_name=r.topic_name,
                    total_attempts=t_total,
                    correct_attempts=t_correct,
                    accuracy_percentage=round(t_acc, 2),
                )
            )

        return UserPerformanceResponse(
            user_id=user_id,
            total_attempts=total,
            correct_attempts=correct,
            accuracy_percentage=round(accuracy, 2),
            avg_time_taken_seconds=round(avg_time, 2),
            topic_breakdown=topic_stats,
        )

    @staticmethod
    def to_topic_revision_recommendations(
        user_id: int,
        attempted_topic_rows: Any,  # noqa: ANN401
        unattempted_topics: Any,  # noqa: ANN401
        limit: int = 5,
    ) -> TopicRevisionResponse:
        """Production multi-factor algorithm calculating topic revision priorities and reasons."""
        scored_topics: list[tuple[float, dict[str, Any]]] = []
        now = datetime.now(UTC)

        # 1. Evaluate attempted topics
        for r in attempted_topic_rows:
            t_total = r.total_attempts or 0
            t_correct = r.correct_attempts or 0
            t_incorrect = t_total - t_correct
            t_acc = (t_correct / t_total * 100.0) if t_total > 0 else 0.0

            # Calculate time decay
            last_attempt_at: datetime | None = getattr(r, "last_attempted_at", None)
            days_since = (now - last_attempt_at).days if last_attempt_at else 0

            # Signal scoring & reason determination
            if t_acc < 50.0:
                score = (100.0 - t_acc) * 1.5 + (t_incorrect * 2.0)
                reason = f"Low accuracy ({round(t_acc, 1)}%)"
            elif t_incorrect >= 3:
                score = 70.0 + (t_incorrect * 3.0)
                reason = f"Repeated incorrect attempts ({t_incorrect} errors)"
            elif days_since >= 14:
                score = 50.0 + min(days_since, 30)
                reason = f"Long time since last review ({days_since} days ago)"
            else:
                score = 100.0 - t_acc
                reason = f"Needs periodic review ({round(t_acc, 1)}% accuracy)"

            scored_topics.append(
                (
                    score,
                    {
                        "topic_id": r.topic_id,
                        "topic_name": r.topic_name,
                        "accuracy_percentage": round(t_acc, 1),
                        "total_attempts": t_total,
                        "correct_attempts": t_correct,
                        "last_attempted_at": last_attempt_at,
                        "reason": reason,
                    },
                )
            )

        # 2. Evaluate unattempted topics (Cold Start)
        for t in unattempted_topics:
            scored_topics.append(
                (
                    85.0,  # High priority for new unattempted topics
                    {
                        "topic_id": t.id,
                        "topic_name": t.name,
                        "accuracy_percentage": 0.0,
                        "total_attempts": 0,
                        "correct_attempts": 0,
                        "last_attempted_at": None,
                        "reason": "Unattempted topic — needs initial practice",
                    },
                )
            )

        # 3. Sort by priority score DESCENDING
        scored_topics.sort(key=lambda item: item[0], reverse=True)

        # 4. Take top N (default 5) and assign priority 1..N
        recommendations: list[TopicRevisionRecommendation] = []
        for idx, (_, data) in enumerate(scored_topics[:limit]):
            recommendations.append(
                TopicRevisionRecommendation(
                    topic_id=data["topic_id"],
                    topic=data["topic_name"],
                    priority=idx + 1,
                    reason=data["reason"],
                    accuracy_percentage=data["accuracy_percentage"],
                    total_attempts=data["total_attempts"],
                    correct_attempts=data["correct_attempts"],
                    last_attempted_at=data["last_attempted_at"],
                )
            )

        return TopicRevisionResponse(user_id=user_id, recommendations=recommendations)
