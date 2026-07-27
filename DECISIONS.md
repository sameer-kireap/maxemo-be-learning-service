# Architectural Decision Records (ADRs)

This document formally records all major technical and design decisions made during the development of the **Maxemo Learning Analytics Microservice**.

---

## Decision Index

1. [ADR-001: Choice of PostgreSQL 16 as Relational Database](#adr-001-choice-of-postgresql-16-as-relational-database)
2. [ADR-002: Choice of FastAPI Web Framework](#adr-002-choice-of-fastapi-web-framework)
3. [ADR-003: Choice of Clean Architecture Structure](#adr-003-choice-of-clean-architecture-structure)
4. [ADR-004: Choice of Repository Pattern with BaseRepository & QueryBuilder](#adr-004-choice-of-repository-pattern-with-baserepository--querybuilder)
5. [ADR-005: Choice of Primary Key Strategy (UUID vs. BigInt)](#adr-005-choice-of-primary-key-strategy-uuid-vs-bigint)
6. [ADR-006: Server-Side Derived Option Correctness](#adr-006-server-side-derived-option-correctness)
7. [ADR-007: Stateless Dynamic Performance Calculation](#adr-007-stateless-dynamic-performance-calculation)
8. [ADR-008: Omission of Redis Cache in Phase 1](#adr-008-omission-of-redis-cache-in-phase-1)
9. [ADR-009: Omission of Asynchronous Message Queues / Background Workers](#adr-009-omission-of-asynchronous-message-queues--background-workers)
10. [ADR-010: Window Function (`COUNT(*) OVER()`) Single-Query Pagination](#adr-010-window-function-count-over-single-query-pagination)

---

### ADR-001: Choice of PostgreSQL 16 as Relational Database

- **Problem**: Need a robust, ACID-compliant database to store relational question/topic models, structured options (`JSONB`), and high-volume user attempt analytics.
- **Options Considered**:
  1. PostgreSQL 16
  2. MongoDB / Document Store
  3. MySQL 8.0
- **Decision**: **PostgreSQL 16**.
- **Pros**: Native `JSONB` array support for MCQ options, window function support for single-query pagination (`COUNT(*) OVER()`), schema isolation via `learning_schema`, and superior index support (GIN, B-Tree).
- **Cons**: Requires database connection pooling management under high concurrency.
- **Trade-Offs**: Relational integrity and transaction guarantees prioritized over schemaless document flexibility.

---

### ADR-002: Choice of FastAPI Web Framework

- **Problem**: Require an asynchronous ASGI Python web framework with low overhead, native async/await support, automatically generated OpenAPI schemas, and strict request validation.
- **Options Considered**:
  1. FastAPI
  2. Django REST Framework (DRF)
  3. Flask / Quart
- **Decision**: **FastAPI**.
- **Pros**: Built on Pydantic v2 and Starlette, native type annotation validation, sub-millisecond route dispatch overhead, automatic Swagger UI generation.
- **Cons**: Requires explicit architecture discipline (unlike Django's "batteries-included" monolith).
- **Trade-Offs**: High performance and async integration selected over framework-managed admin panels.

---

### ADR-003: Choice of Clean Architecture Structure

- **Problem**: Need to structure application code so domain rules and business logic remain isolated from database frameworks, web frameworks, and external dependencies.
- **Options Considered**:
  1. Clean Architecture (Layered Presentation/Service/Repository)
  2. Django-Style Monolithic App Structure
  3. Anemic Scripting Approach
- **Decision**: **Clean Architecture**.
- **Pros**: Business logic in `app/service/` is testable in isolation using unit tests without needing a running database; interfaces (`app/interface/`) define explicit domain contracts.
- **Cons**: Higher upfront boilerplates (interfaces, DTOs, mappers).
- **Trade-Offs**: Maintainability, testability, and enterprise readability prioritized over initial prototyping speed.

---

### ADR-004: Choice of Repository Pattern with BaseRepository & QueryBuilder

- **Problem**: Routers and services shouldn't construct raw ORM SQL queries or manage pagination boilerplates directly.
- **Options Considered**:
  1. Generic `BaseRepository[T]` with `QueryBuilder`
  2. Direct ORM calls inside FastAPI Service/Router functions
  3. Active Record Pattern (models managing own queries)
- **Decision**: **Generic `BaseRepository[T]` + `QueryBuilder`**.
- **Pros**: Encapsulates pagination, filtering, searching, and sorting into a reusable method (`list_generic`). Allows single-query window count execution.
- **Cons**: Adds abstraction layer over SQLAlchemy ORM.
- **Trade-Offs**: Strict DRY (Don't Repeat Yourself) data access enforcement across all entities.

---

### ADR-005: Choice of Primary Key Strategy (UUID vs. BigInt)

- **Problem**: Select appropriate primary key types for `topics`, `questions`, and `attempts`.
- **Options Considered**:
  1. UUID v4 for all entities
  2. Auto-incrementing BigInt for all entities
  3. Hybrid Strategy: UUID for public entities (`topics`, `questions`), BigInt for high-volume logs (`attempts`)
- **Decision**: **UUID for `topics` and `questions`; BigInt for `user_id` external integration**.
- **Pros**: UUID prevents ID enumeration attacks on public API endpoints (`/questions/e8f4362e...`). Allows distributed client-side ID generation.
- **Cons**: UUIDs consume 16 bytes compared to 8 bytes for BigInt, resulting in slightly larger B-Tree index sizes.
- **Trade-Offs**: Security against enumeration attacks prioritized for public domain entities.

---

### ADR-006: Server-Side Derived Option Correctness

- **Problem**: Prevent malicious clients from forging `is_correct: true` in attempt submission requests.
- **Options Considered**:
  1. Client passes `is_correct` in JSON payload
  2. Server derives `is_correct` by comparing `selected_option_index` with `question.correct_option_index`
- **Decision**: **Server-Side Derived Correctness**.
- **Pros**: Guarantees zero security compromise or score tampering.
- **Cons**: Requires fetching the target `Question` entity from DB during attempt submission.
- **Trade-Offs**: Data integrity and security prioritized over saving a single indexed DB lookup.

---

### ADR-007: Stateless Dynamic Performance Calculation

- **Problem**: How to calculate user accuracy summary percentages and topic breakdowns.
- **Options Considered**:
  1. Compute dynamically via SQL aggregate queries on `question_attempts`
  2. Maintain pre-aggregated counter fields in a `user_performance` table updated on every submit
- **Decision**: **Stateless Dynamic Calculation**.
- **Pros**: Zero possibility of state drift, stale counters, or write-lock contention during concurrent submissions.
- **Cons**: Requires DB aggregation on read requests.
- **Trade-Offs**: Accuracy and concurrency safety prioritized over read query cost (mitigated by index `ix_attempts_user_question_correct`).

---

### ADR-008: Omission of Redis Cache in Phase 1

- **Problem**: Determine whether an in-memory Redis cache is required for initial MVP deployment.
- **Options Considered**:
  1. Include Redis caching layer for `/questions` and `/topics`
  2. Omit Redis and rely on PostgreSQL buffer cache & indexed queries
- **Decision**: **Omit Redis in Phase 1**.
- **Pros**: Simple deployment, zero cache invalidation bugs, lower infrastructure cost.
- **Cons**: Higher DB read query traffic under massive load (> 10,000 RPS).
- **Trade-Offs**: Avoided premature optimization for initial deployment phase.

---

### ADR-009: Omission of Asynchronous Message Queues / Background Workers

- **Problem**: Decide whether attempt submission should be written to Kafka/RabbitMQ asynchronously.
- **Options Considered**:
  1. Synchronous HTTP write directly to PostgreSQL inside FastAPI transaction
  2. Async write to RabbitMQ/Kafka + Celery background worker consuming attempts
- **Decision**: **Synchronous HTTP Write to PostgreSQL**.
- **Pros**: Learner receives immediate feedback (`is_correct: true/false`) in the HTTP response body. Zero eventual consistency lag.
- **Cons**: Attempt submission response latency is bound to DB disk write flush.
- **Trade-Offs**: Instant UX response feedback prioritized over queue-decoupled writes.

---

### ADR-010: Window Function (`COUNT(*) OVER()`) Single-Query Pagination

- **Problem**: Traditional pagination executes two SQL queries: `SELECT COUNT(*)` followed by `SELECT * LIMIT offset`.
- **Options Considered**:
  1. Two DB queries (`COUNT(*)` then `SELECT LIMIT`)
  2. Single SQL Query with `COUNT(*) OVER()` window function
- **Decision**: **Single SQL Query with `COUNT(*) OVER()`**.
- **Pros**: Cuts database network roundtrips in half (1 DB call instead of 2).
- **Cons**: Requires extracting `total_count` from the first row of result sets.
- **Trade-Offs**: Substantial query latency reduction achieved with minimal repository processing code.
