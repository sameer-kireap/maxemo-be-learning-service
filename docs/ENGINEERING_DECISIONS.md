# Engineering Decisions & Strategic Architecture Review ⚙️

## Executive Summary

This document provides formal responses to technical assignment review questions from a Senior/Principal Engineer perspective.

---

## 1. Database Design & Data Access Strategy 🗄️

### Key Architectural Choices

1. **Schema Isolation (`learning_schema`)**:
   All entity tables (`topics`, `questions`, `question_attempts`, `question_topics`) reside strictly within `learning_schema`. This enables shared database hosting alongside other enterprise services without namespace collisions.

2. **Relational Normalized Core & Foreign Key Constraints**:
   A clean Many-to-Many junction table (`question_topics`) links questions and topics with `ON DELETE CASCADE` referential integrity rules, ensuring orphan records are automatically prevented upon entity deletion.

3. **`JSONB` Arrays for Question Options**:
   MCQ option text strings are stored as a `JSONB` array directly in `questions.options`. This avoids creating an ancillary `question_options` child table, eliminating unnecessary JOIN latency during question retrieval while preserving document query capabilities.

4. **Immutable Time-Series Attempt Logging**:
   Learner attempts are recorded as immutable time-series rows in `question_attempts`. This enables granular temporal analytics, historical accuracy tracking, and algorithmic revision recommendations.

5. **Modular Generic List Architecture (`BaseRepository[T]` & `QueryBuilder`)**:
   - **Requirement**: Enterprise list endpoints require filtering, free-text ILIKE search, type-safe sorting, and offset/limit pagination.
   - **Implementation**: Every repository inherits from `BaseRepository[T]`. The reusable method `list_generic()` delegates dynamic query construction to `QueryBuilder`, mapping filter dictionaries, search columns, and type-safe `StrEnum` sort fields (`QuestionSortField`, `TopicSortField`) with zero code duplication across domain repositories.

6. **Single Database Hit Window Function (`COUNT(*) OVER()`)**:
   - **Traditional Problem**: Standard pagination requires 2 database roundtrips—a `SELECT COUNT(*)` count query followed by a `SELECT * LIMIT offset` data query.
   - **Engineered Solution**: `BaseRepository.list_generic()` attaches `COUNT(*) OVER()` window functions to the primary select query. PostgreSQL returns both the paginated entity slice and the total unpaginated record count in a **single database hit**, cutting database network roundtrips in half.

---

### Indexing Strategy Overview

> 📖 **Full Index Specification**: For complete DDL index statements, index-only scan execution mechanics, and index justifications, see **[`DATABASE.md`](./DATABASE.md)**.

- **Composite B-Tree Index `ix_attempts_user_question_correct (user_id, question_id, is_correct)`**:
  Enables index-only scans for user performance calculations (`GET /users/{id}/performance`) and revision recommendations without scanning table heap pages.

- **Single-Column B-Tree Indexes**:
  Applied on `topics.name` (Unique), `questions.difficulty`, `question_attempts.user_id`, `question_attempts.question_id`, and `question_attempts.created_at DESC`.

---

## 2. What Was Intentionally Not Built 🧱

To deliver a production-grade microservice within a 2-day timeframe without over-engineering:

1. **Redis Caching Layer**: Avoided cache invalidation complexity in Phase 1. PostgreSQL B-Tree indexes serve queries in < 5ms.

2. **Asynchronous Message Queue (Kafka/RabbitMQ)**: Direct HTTP writes to PostgreSQL provide instant `is_correct` feedback in the response body.

3. **Complex User Auth / JWT Decoding**: The API accepts `user_id` in paths and payloads, decoupling authorization from domain learning logic.
