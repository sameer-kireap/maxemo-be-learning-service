"""End-to-end API integration tests for endpoints and APIResponse payload wrappers."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_topics_api_flow(client: AsyncClient) -> None:
    unique_name = f"Pulmonology-{uuid.uuid4().hex[:6]}"
    # 1. Create topic
    response = await client.post("/api/v1/topics", json={"name": unique_name})
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == unique_name
    topic_id = data["data"]["id"]

    # 2. Duplicate topic creation fails with 409
    dup_res = await client.post("/api/v1/topics", json={"name": unique_name})
    assert dup_res.status_code == 409
    dup_data = dup_res.json()
    assert dup_data["error"]["code"] == "TOPIC_ALREADY_EXISTS"

    # 3. Get topic by ID
    get_res = await client.get(f"/api/v1/topics/{topic_id}")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["name"] == unique_name

    # 4. List topics paginated
    list_res = await client.get("/api/v1/topics?offset=0&limit=10")
    assert list_res.status_code == 200
    list_data = list_res.json()["data"]
    assert list_data["total_records"] >= 1
    assert any(t["id"] == topic_id for t in list_data["items"])


@pytest.mark.asyncio
async def test_questions_and_attempts_api_flow(client: AsyncClient) -> None:
    unique_topic = f"Immunology-{uuid.uuid4().hex[:6]}"
    # 1. Create Topic
    t_res = await client.post("/api/v1/topics", json={"name": unique_topic})
    topic_id = t_res.json()["data"]["id"]

    # 2. Create Question
    q_payload = {
        "text": "Which cell produces antibodies?",
        "options": ["T cell", "B cell", "Macrophage", "Neutrophil"],
        "correct_option_index": 1,
        "difficulty": "medium",
        "topic_ids": [topic_id],
    }
    q_res = await client.post("/api/v1/questions", json=q_payload)
    assert q_res.status_code == 201
    q_data = q_res.json()["data"]
    question_id = q_data["id"]
    assert q_data["correct_option_index"] == 1

    # 3. Learner View (excludes correct_option_index)
    learner_res = await client.get(f"/api/v1/questions/{question_id}")
    assert learner_res.status_code == 200
    learner_data = learner_res.json()["data"]
    assert "correct_option_index" not in learner_data
    assert learner_data["text"] == "Which cell produces antibodies?"

    # 4. Submit Attempt (Server-derived is_correct)
    user_id = 8881
    att_res = await client.post(
        "/api/v1/attempts",
        json={
            "user_id": user_id,
            "question_id": question_id,
            "selected_option_index": 1,
            "time_taken_seconds": 12,
        },
    )
    assert att_res.status_code == 201
    att_data = att_res.json()["data"]
    assert att_data["is_correct"] is True

    # 5. Performance Analytics
    perf_res = await client.get(f"/api/v1/performance/users/{user_id}")
    assert perf_res.status_code == 200
    perf_data = perf_res.json()["data"]
    assert perf_data["user_id"] == user_id
    assert perf_data["total_attempts"] >= 1

    # 6. Practice Mode
    prac_res = await client.get(f"/api/v1/questions/practice?topic_ids={topic_id}&limit=5")
    assert prac_res.status_code == 200
    assert len(prac_res.json()["data"]) >= 1
