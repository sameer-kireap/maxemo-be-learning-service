# Engineering Decisions & Strategic Architecture Review

This document provides formal responses to the technical assignment review questions from a Senior/Principal Engineer perspective.

---

## 1. Database Design Strategy

### Design Choices
- **PostgreSQL 16 with `learning_schema`**: Table structures are explicitly scoped inside `learning_schema` to allow shared database hosting alongside other enterprise services without namespace collisions.
- **Relational Normalized Core**: Many-to-many relationship between `questions` and `topics` via `question_topics` junction table with `ON DELETE CASCADE` rules.
- **`JSONB` for Question Options**: Storing MCQ option text arrays as `JSONB` in the `questions` table avoids creating a redundant `question_options` child table, reducing JOIN complexity for simple option list retrieval.
- **Separate `question_attempts` Table**: Every attempt is recorded as an immutable time-series row. This enables granular temporal analytics, historical accuracy tracking, and algorithmic revision recommendations.

### Indexing Strategy
- **Composite Index `(user_id, question_id, is_correct)`**: Supports index-only scans for aggregate user performance queries and revision recommendations without touching row data pages.
- **Single-Column Indexes**: B-Tree indexes on `questions.difficulty`, `topics.name` (Unique), and `question_attempts.created_at`.

---

## 2. Revision Recommendation Algorithm

### Algorithm Overview
The revision engine prioritizes questions based on historical learner accuracy:

$$\text{Accuracy}(u, q_k) = \frac{\text{Correct Attempts}}{\text{Total Attempts}}$$

Questions are ranked by **Accuracy ASCENDING**, with ties broken by **`created_at` DESCENDING** (most recently attempted weak questions first).

### Why Selected Over Machine Learning (ML)
1. **Deterministic Execution**: Predictable, transparent scoring that can be explained directly to learners.
2. **Zero Infrastructure Overhead**: No ML feature stores, model training pipelines, or inferencing latency.
3. **Sub-5ms Latency**: Executes directly in PostgreSQL using indexed SQL aggregation.

---

## 3. What Was Intentionally Not Built

To deliver a production-grade microservice within a 2-day timeframe without over-engineering:

1. **Redis Caching Layer**: Avoided cache invalidation complexity in Phase 1. PostgreSQL B-Tree indexes serve queries in < 5ms.
2. **Asynchronous Message Queue (Kafka/RabbitMQ)**: Direct HTTP writes to PostgreSQL provide instant `is_correct` feedback in the response body.
3. **Complex User Auth / JWT Decoding**: The API accepts `user_id` in paths and payloads, decoupling authorization from domain learning logic.

---

## 4. What Would Be Improved with Another Day

If granted an additional development day, the following enhancements would be prioritized:

1. **PgBouncer Connection Pooling**: Deploy PgBouncer in front of PostgreSQL to handle 5,000+ concurrent DB connections seamlessly.
2. **OpenTelemetry & Prometheus Instrumentation**: Add metric counters (`http_requests_total`) and distributed tracing for full APM observability.
3. **Exponential Decay in Revision Algorithm**: Incorporate time decay so recent mistakes carry more weight than mistakes made months ago.

---

## 5. Product Requirement Change Analysis

> **Requirement Change**: *"How would the system change if exams within 30 days require different recommendations?"*

### Scenario Analysis
If a learner has an upcoming exam within 30 days, their revision priority must shift from general weak points to **high-yield exam-relevant topics** and **exam-specific question pools**.

### A. Schema Changes
To support exam dates and exam-topic mappings, two new tables are added:

```sql
-- 1. Learner Exam Schedules
CREATE TABLE learning_schema.user_exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    exam_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_user_exams_user_date ON learning_schema.user_exams (user_id, exam_date);

-- 2. Exam Topic High-Yield Weightings
CREATE TABLE learning_schema.exam_topic_weights (
    exam_name VARCHAR(255) NOT NULL,
    topic_id UUID NOT NULL REFERENCES learning_schema.topics(id) ON DELETE CASCADE,
    weight_multiplier FLOAT NOT NULL DEFAULT 1.0,
    PRIMARY KEY (exam_name, topic_id)
);
```

### B. Algorithmic Changes
The scoring formula transitions to a **Urgency-Weighted Priority Score**:

$$\text{DaysToExam} = \text{exam\_date} - \text{current\_date}$$

$$\text{UrgencyWeight} = \begin{cases} 
2.5 & \text{if } \text{DaysToExam} \le 30 \\
1.0 & \text{otherwise}
\end{cases}$$

$$\text{PriorityScore}(u, q_k) = \left(1.0 - \text{Accuracy}(u, q_k)\right) \times \text{UrgencyWeight} \times \text{TopicWeight}(q_k)$$

Questions with the **highest `PriorityScore`** are recommended first.

### C. Migration & Rollout Strategy
1. **Alembic Non-Breaking Migration**: Add `user_exams` and `exam_topic_weights` tables without altering existing tables.
2. **Backward Compatibility**: If a learner has no exam within 30 days (`user_exams` query returns null), the algorithm falls back to the original accuracy-based ranking.
3. **Feature Flag Rollout**: Enable exam-weighted recommendations behind a feature flag (`ENABLE_EXAM_DRIVEN_REVISION=true`).
