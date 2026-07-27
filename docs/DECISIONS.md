# Architectural Decision Records (ADRs) 📜

## Executive Summary

This document formally records all key architectural and engineering decisions made during the development of the **Maxemo Learning Analytics Microservice**.

---

## Decision Index 📋

1. [ADR-001: Choice of Clean Architecture Layered Structure](#adr-001-choice-of-clean-architecture-layered-structure)
2. [ADR-002: Choice of Generic Repository Pattern & QueryBuilder](#adr-002-choice-of-generic-repository-pattern--querybuilder)
3. [ADR-003: Choice of Primary Key Strategy (UUID vs. BigInt)](#adr-003-choice-of-primary-key-strategy-uuid-vs-bigint)
4. [ADR-004: Server-Side Derived Option Correctness](#adr-004-server-side-derived-option-correctness)
5. [ADR-005: Stateless Dynamic Performance Calculation](#adr-005-stateless-dynamic-performance-calculation)
6. [ADR-006: Omission of Redis Cache in Phase 1](#adr-006-omission-of-redis-cache-in-phase-1)
7. [ADR-007: Omission of Asynchronous Message Queues in Phase 1](#adr-007-omission-of-asynchronous-message-queues-in-phase-1)
8. [ADR-008: Window Function (`COUNT(*) OVER()`) Single-Query Pagination](#adr-008-window-function-count-over-single-query-pagination)

---

### ADR-001: Choice of Clean Architecture Layered Structure

- **Problem**: Need to structure application code so domain rules and business logic remain isolated from database frameworks, web frameworks, and external dependencies.

- **Options Considered**:
  1. Clean Architecture (Layered Presentation/Service/Repository)
  2. Monolithic Django-Style Structure
  3. Scripting Approach

- **Decision**: **Clean Architecture**.

- **Pros**: Business logic in `app/service/` is testable in isolation using unit tests without needing a running database; interfaces (`app/interface/`) define explicit domain contracts.

- **Cons**: Higher upfront boilerplates (interfaces, DTOs, mappers).

- **Trade-Offs**: Maintainability, testability, and enterprise readability prioritized over initial prototyping speed.

---

### ADR-002: Choice of Generic Repository Pattern & QueryBuilder

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

### ADR-003: Choice of Primary Key Strategy (UUID vs. BigInt)

- **Problem**: Select appropriate primary key types for `topics`, `questions`, and `attempts`.

- **Options Considered**:
  1. UUID v4 for all entities
  2. Auto-incrementing BigInt for all entities
  3. Hybrid Strategy: UUID for public domain entities (`topics`, `questions`), BigInt for external integration (`user_id`)

- **Decision**: **UUID for `topics` and `questions`; BigInt for `user_id` external integration**.

- **Pros**: UUID prevents ID enumeration attacks on public API endpoints (`/questions/e8f4362e...`). Allows distributed client-side ID generation.

- **Cons**: UUIDs consume 16 bytes compared to 8 bytes for BigInt, resulting in slightly larger B-Tree index sizes.

- **Trade-Offs**: Security against enumeration attacks prioritized for public domain entities.

---

### ADR-004: Server-Side Derived Option Correctness

- **Problem**: Prevent malicious clients from forging `is_correct: true` in attempt submission requests.

- **Options Considered**:
  1. Client passes `is_correct` in JSON payload
  2. Server derives `is_correct` by comparing `selected_option_index` with `question.correct_option_index`

- **Decision**: **Server-Side Derived Correctness**.

- **Pros**: Guarantees zero security compromise or score tampering.

- **Cons**: Requires fetching the target `Question` entity from DB during attempt submission.

- **Trade-Offs**: Data integrity and security prioritized over saving a single indexed DB lookup.

---

### ADR-005: Stateless Dynamic Performance Calculation

- **Problem**: How to calculate user accuracy summary percentages and topic breakdowns.

- **Options Considered**:
  1. Compute dynamically via SQL aggregate queries on `question_attempts`
  2. Maintain pre-aggregated counter fields in a `user_performance` table updated on every submit

- **Decision**: **Stateless Dynamic Calculation**.

- **Pros**: Zero possibility of state drift, stale counters, or write-lock contention during concurrent submissions.

- **Cons**: Requires DB aggregation on read requests.

- **Trade-Offs**: Accuracy and concurrency safety prioritized over read query cost (mitigated by index `ix_attempts_user_question_correct`).

---

### ADR-006: Omission of Redis Cache in Phase 1

- **Problem**: Determine whether an in-memory Redis cache is required for initial MVP deployment.

- **Options Considered**:
  1. Include Redis caching layer for `/questions` and `/topics`
  2. Omit Redis and rely on PostgreSQL buffer cache & indexed queries

- **Decision**: **Omit Redis in Phase 1**.

- **Pros**: Simple deployment, zero cache invalidation bugs, lower infrastructure cost.

- **Cons**: Higher DB read query traffic under massive load (> 10,000 RPS).

- **Trade-Offs**: Avoided premature optimization for initial deployment phase.

---

### ADR-007: Omission of Asynchronous Message Queues in Phase 1

- **Problem**: Decide whether attempt submission should be written to Kafka/RabbitMQ asynchronously.

- **Options Considered**:
  1. Synchronous HTTP write directly to PostgreSQL inside FastAPI transaction
  2. Async write to RabbitMQ/Kafka + Celery background worker consuming attempts

- **Decision**: **Synchronous HTTP Write to PostgreSQL**.

- **Pros**: Learner receives immediate feedback (`is_correct: true/false`) in the HTTP response body. Zero eventual consistency lag.

- **Cons**: Attempt submission response latency is bound to DB disk write flush.

- **Trade-Offs**: Instant UX response feedback prioritized over queue-decoupled writes.

---

### ADR-008: Window Function (`COUNT(*) OVER()`) Single-Query Pagination

- **Problem**: Traditional pagination executes two SQL queries: `SELECT COUNT(*)` followed by `SELECT * LIMIT offset`.

- **Options Considered**:
  1. Two DB queries (`COUNT(*)` then `SELECT LIMIT`)
  2. Single SQL Query with `COUNT(*) OVER()` window function

- **Decision**: **Single SQL Query with `COUNT(*) OVER()`**.

- **Pros**: Cuts database network roundtrips in half (1 DB call instead of 2).

- **Cons**: Requires extracting `total_count` from the first row of result sets.

- **Trade-Offs**: Substantial query latency reduction achieved with minimal repository processing code.
