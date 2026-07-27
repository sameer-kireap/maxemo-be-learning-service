# Maxemo Learning Analytics Backend Service

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![uv](https://img.shields.io/badge/uv-managed-purple.svg)](https://github.com/astral-sh/uv)

A high-performance, asynchronous RESTful microservice built with **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0 (AsyncIO)**, and **PostgreSQL 16**.

The service manages medical clinical learning topics, multiple-choice questions (MCQs), learner attempts, accuracy performance analytics, and a performance-driven revision recommendation engine.

---

## Executive Summary (5-Minute Read for Senior Engineers)

This microservice provides a decoupled learning analytics engine designed around **Clean Layered Architecture** and strict **Domain-Driven Design (DDD)** boundaries.

### Key Capabilities
- **Server-Derived Correctness**: MCQ attempt accuracy (`is_correct`) is computed authoritatively on the server side using indexed `correct_option_index` fields. Client payloads cannot spoof or override correctness.
- **Single-Query Window Count Pagination**: All list endpoints execute generic filtering, free-text ILIKE search, type-safe enum sorting, and `COUNT(*) OVER()` window count in a **single database query**, eliminating redundant secondary `SELECT COUNT(*)` roundtrips.
- **Revision Recommendation Engine**: Calculates learner weakness scores per question using database-level accuracy aggregation:
  $$\text{Accuracy} = \frac{\sum \text{Correct Attempts}}{\text{Total Attempts}}$$
  Weakest questions with lowest accuracy are prioritized for targeted revision.
- **Isolated PostgreSQL Schema (`learning_schema`)**: All database tables, custom indexes, and foreign keys are scoped within `learning_schema` to support seamless multi-tenant database co-location.

---

## System Architecture Overview

```
[ Client / Web App ]
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ Presentation Layer (app/api/v1/)                       │
│ - 1-Line DTO Routers (topics, questions, attempts)     │
│ - Root Unversioned Health Check (GET /health)          │
└────────────────────────┬───────────────────────────────┘
                         │ Request / Response DTOs
                         ▼
┌────────────────────────────────────────────────────────┐
│ Service & Domain Layer (app/service/, app/interface/)  │
│ - Abstract Service Interfaces (ITopicService, etc.)    │
│ - Pure Domain Business Logic & Exception Triggers      │
└────────────────────────┬───────────────────────────────┘
                         │ Entities & Query Criteria
                         ▼
┌────────────────────────────────────────────────────────┐
│ Repository Layer (app/repository/, app/utils/)         │
│ - BaseRepository[T] & QueryBuilder                     │
│ - Window Function Pagination & Type-Safe Sort Enums    │
└────────────────────────┬───────────────────────────────┘
                         │ Async Session & Statements
                         ▼
┌────────────────────────────────────────────────────────┐
│ Database Layer (PostgreSQL 16)                         │
│ - learning_schema.topics                               │
│ - learning_schema.questions                            │
│ - learning_schema.question_attempts                    │
│ - learning_schema.question_topics                      │
└────────────────────────────────────────────────────────┘
```

---

## Tech Stack & Tooling

| Component | Tool / Library | Reason for Selection |
|---|---|---|
| **Language** | Python 3.12 | Native `StrEnum`, pattern matching, async performance improvements |
| **Framework** | FastAPI | High-performance ASGI framework with native OpenAPI schema generation |
| **ORM** | SQLAlchemy 2.0 (`asyncpg`) | Modern Type-safe Async ORM with explicit `selectinload` control |
| **Migrations** | Alembic | Version-controlled database schema migration engine |
| **Package Manager** | `uv` (Astral) | Extremely fast Rust-based Python package resolver and environment manager |
| **Database** | PostgreSQL 16 | ACID-compliant relational DB with `jsonb` array indexing & window functions |
| **Linter / Formatter** | Ruff | Lightning-fast Python code linter (sub-millisecond execution) |
| **Static Type Checker** | Mypy | Strict static type checker ensuring type safety across 60+ files |
| **Test Runner** | Pytest (`pytest-asyncio`) | Asynchronous unit and integration test framework |

---

## Project Directory Structure

```
.
├── app/
│   ├── api/                   # Presentation Layer (FastAPI Routers)
│   │   ├── health.py          # Root GET /health endpoint
│   │   └── v1/                # Versioned API routes
│   │       ├── attempts.py    # POST /attempts, GET /attempts/users/{id}/performance
│   │       ├── questions.py   # CRUD /questions, GET /questions/practice
│   │       └── topics.py      # CRUD /topics
│   ├── constant/              # Global constants and Enums (DifficultyLevel, SortOrder)
│   ├── core/                  # Core infrastructure (Config settings, DB engine, Logger)
│   ├── dependencies/          # Modularized FastAPI Dependency Injection providers
│   ├── exception/             # Domain-specific CustomExceptions & Global Error Handlers
│   ├── interface/             # Abstract Interface Contracts (ITopicService, IQuestionService)
│   ├── mapper/                # DTO ↔ Entity Transformation Mappers
│   ├── model/                 # SQLAlchemy 2.0 ORM Models & Mixins
│   ├── repository/            # Generic & Concrete Data Access Repositories
│   ├── schema/                # Pydantic DTO Validation Schemas
│   ├── service/               # Pure Business Domain Service Implementations
│   └── utils/                 # QueryBuilder helper utilities
├── scripts/                   # CLI Seeder Scripts (seed_db.py, seed_attempts.py)
├── tests/                     # Test Suite (unit, integration, repositories, services, API)
├── migrations/                # Alembic Database Migration Revisions
├── Dockerfile                 # Multi-stage production Dockerfile
├── docker-compose.yml         # Container orchestration configuration
├── docker-entrypoint.sh       # Container entrypoint with automatic Alembic migration execution
└── pyproject.toml             # Project manifest and dependency declarations
```

---

## Quick Start & Local Development

### Prerequisites
- Python 3.12+
- `uv` (Fast Python package installer): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- PostgreSQL 16 (or Docker Desktop)

### 1. Environment Setup
Clone the repository and copy the environment template:
```bash
cp .env.example .env
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Spin Up PostgreSQL via Docker
```bash
docker compose up -d postgres
```

### 4. Run Database Migrations
```bash
uv run alembic upgrade head
```

### 5. Seed Master Data & Test Attempts
```bash
# Seed master Topics and Clinical MCQs
uv run python -m scripts.seed_db

# Seed test learner attempts for user_id 101, 102, 103
uv run python -m scripts.seed_attempts --user-id 101 102 103
```

### 6. Start Local Application Server
```bash
uv run uvicorn app.main:app --reload --port 8000
```
Access the interactive OpenAPI Documentation at: **`http://localhost:8000/docs`**

---

## Running with Docker Compose (Production Environment)

To build and run the entire microservice stack (App + PostgreSQL) in isolated Docker containers:

```bash
docker compose up -d --build
```

- **Health Check Verification**:
  ```bash
  curl http://localhost:8000/health
  ```
  *Response:*
  ```json
  {
    "success": true,
    "message": "Service is operational",
    "data": {
      "status": "healthy",
      "service": "Learning Analytics Service",
      "version": "1.0.0"
    },
    "error": null
  }
```

---

## Running Test Suite & Quality Checks

The repository enforces 100% clean static analysis and passing integration tests:

```bash
# 1. Run Ruff Linter
uv run ruff check app/ scripts/ tests/

# 2. Run Mypy Static Type Verification
uv run mypy app/ scripts/

# 3. Run Pytest Integration Test Suite
uv run pytest tests/ -v
```

---

## Key Engineering Decisions & Trade-Offs

1. **Stateless On-Demand Analytics**: Performance percentages and revision recommendations are computed dynamically via SQL aggregation rather than stored state. This guarantees zero state drift at the cost of higher CPU query cost on high attempt volumes (mitigated by indexed `(user_id, question_id)` composite B-tree keys).
2. **Server-Derived Correctness**: Learner submissions pass `selected_option_index` only. The server compares this against `question.correct_option_index` to compute `is_correct`, eliminating client-side cheating vectors.
3. **No In-Memory Cache (Redis) in Phase 1**: Intentionally omitted Redis caching to maintain transaction simplicity and avoid cache invalidation overhead. Caching strategy is documented in `SCALABILITY.md` for scaling beyond $10,000$ RPS.

---

## Architecture & Engineering Documentation Index

- [`ARCHITECTURE.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/ARCHITECTURE.md): Deep-dive into Clean Architecture layers, request lifecycle, DI, and domain boundaries.
- [`DATABASE.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/DATABASE.md): ER diagram, schema constraints, indexes, query patterns, and database scaling strategy.
- [`DECISIONS.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/DECISIONS.md): Architectural Decision Records (ADRs) justifying technology choices and trade-offs.
- [`REVISION_ALGORITHM.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/REVISION_ALGORITHM.md): In-depth mathematical analysis of the revision recommendation algorithm.
- [`SCALABILITY.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/SCALABILITY.md): Bottleneck analysis, read replicas, partitioning, Redis caching, and Kafka async streaming.
- [`API_DESIGN.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/API_DESIGN.md): RESTful contract specifications, payload examples, error schema, and HTTP status code mappings.
- [`TESTING.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/TESTING.md): Testing strategy, test isolation, fixtures, and mock session injection.
- [`ENGINEERING_DECISIONS.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/ENGINEERING_DECISIONS.md): Responses to formal architectural review questions.
- [`ASSIGNMENT_NOTES.md`](file:///Users/chemmi/Desktop/maxemo-qns-be-service/ASSIGNMENT_NOTES.md): Traceability matrix verifying 100% compliance with prompt requirements.

---

## License

Distributed under the MIT License. See `LICENSE` for details.
