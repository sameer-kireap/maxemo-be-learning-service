# Maxemo Learning Analytics Backend Service

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

A high-performance, production-grade RESTful microservice built with **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0 (AsyncIO)**, and **PostgreSQL 16**.

The service manages medical clinical topics (*Cardiology*, *Renal Pathology*, *Pharmacology*, *Microbiology*), clinical multiple-choice questions (MCQs), learner attempts, accuracy analytics, and a personalized topic revision queue.

---

## 📋 Table of Contents

1. [Architecture & System Design](#1-architecture--system-design)
2. [Domain Models & Relationships](#2-domain-models--relationships)
3. [API Endpoints](#3-api-endpoints)
4. [Personalized Topic Revision Algorithm](#4-personalized-topic-revision-algorithm)
5. [Engineering Decisions & Trade-Offs](#5-engineering-decisions--trade-offs)
6. [Strategic Product Roadmap](#6-strategic-product-roadmap)
7. [Product Requirement Changes: 30-Day Exam Scenario](#7-product-requirement-changes-30-day-exam-scenario)
8. [Scale Scenario: 10M Attempts Scaling Strategy](#8-scale-scenario-10m-attempts-scaling-strategy)
9. [Quick Start & Local Setup](#9-quick-start--local-setup)
10. [Docker Deployment](#10-docker-deployment)
11. [Testing & Quality Assurance](#11-testing--quality-assurance)
12. [Architectural Decision Records (ADRs)](#12-architectural-decision-records-adrs)
13. [AI Tools Used](#13-ai-tools-used)

---

## 1. 🏗️ Architecture & System Design

> 📖 **Full Architecture Specification**: For complete layer topology diagrams, execution sequence diagrams, and dependency injection graphs, see **[`ARCHITECTURE.md`](./docs/ARCHITECTURE.md)**.

The microservice is constructed using **Clean Layered Architecture** and strict **Domain-Driven Design (DDD)** boundaries:

1. **Strict Layer Isolation**: API routers (`app/api/`) contain zero business logic or raw SQL queries; they only parse DTO payloads and delegate directly to domain services.

2. **Decoupled Business Domain Rules**: Business invariants and scoring logic reside in pure domain services (`app/service/`), testable in isolation without a running database.

3. **Encapsulated Repository Layer**: Database interaction is isolated inside repositories (`app/repository/`) using `BaseRepository[T]` and `QueryBuilder`, keeping ORM logic separated from HTTP controllers.

4. **Automated Dependency Injection**: FastAPI `Depends()` resolves async DB sessions, repositories, and services into route handlers prior to request execution (`app/dependencies/`).

5. **Unified Response & Error Envelopes**: All successful responses and domain exceptions are intercepted and formatted as standard `APIResponse[T]` payloads.

---

## 2. 🗄️ Domain Models & Relationships

> 📖 **Full Database Specification**: For complete ER diagrams, table schemas, foreign key constraints, indexes, and SQL query patterns, see **[`DATABASE.md`](./docs/DATABASE.md)**.

The data model is implemented in PostgreSQL inside an isolated schema (**`learning_schema`**) containing 4 primary relational entities:

- **`topics`**: Learning subjects (*Cardiology*, *Renal Pathology*, *Pharmacology*, *Microbiology*) with unique name constraints.

- **`questions`**: Clinical multiple-choice questions containing text stems, `jsonb` options array, `correct_option_index`, and difficulty ratings (`easy`, `medium`, `hard`).

- **`question_topics`**: Junction table supporting **Many-to-Many** relationships (a single question can belong to multiple topics).

- **`question_attempts`**: Immutable time-series log recording every learner attempt with `user_id`, `question_id`, server-derived `is_correct`, `time_taken_seconds`, and timestamp.

---

## 3. 🔌 API Endpoints

> 📖 **Full API Specification**: For complete REST contracts, JSON payloads, query parameters, validation rules, and status code mappings, see **[`API_DESIGN.md`](./docs/API_DESIGN.md)**.

All endpoints return a standardized JSON envelope (`APIResponse[T]`):

| Method | Endpoint | Description | Key Business Logic / Security |
|---|---|---|---|
| **`POST`** | `/api/v1/attempts` | Record a question attempt | **Server-Derived Correctness**: `is_correct` evaluated authoritatively on server |
| **`GET`** | `/api/v1/users/{id}/performance` | Learner performance breakdown | Dynamic SQL aggregate calculation of per-topic attempted, correct, & accuracy % |
| **`GET`** | `/api/v1/users/{id}/revision` | Topic revision queue | Recommends top ~5 weak topics with priority ranks & explainable reasons |
| **`GET`** | `/api/v1/users/{id}/revision/questions` | Question revision queue | Recommends weak questions sorted by accuracy |
| **`POST`** | `/api/v1/topics` | Create a learning topic | Enforces unique topic name (HTTP 409 Conflict) |
| **`GET`** | `/api/v1/topics` | List topics paginated | Single-query window count (`COUNT(*) OVER()`), filtering & sorting |
| **`POST`** | `/api/v1/questions` | Create a clinical question | Validates option index bounds; supports multi-topic linkage |
| **`GET`** | `/api/v1/questions/{id}` | Get question (Learner View) | Excludes `correct_option_index` to prevent client-side cheating |
| **`GET`** | `/health` | Service health check | Root unversioned endpoint returning operational status and version |

---

## 4. 📐 Personalized Topic Revision Algorithm

> 📖 **Complete Specification Document**: For the full decision tree diagram, real-world case breakdowns, and mathematical proof, see **[`REVISION_ALGORITHM.md`](./docs/REVISION_ALGORITHM.md)**.

### Production Multi-Factor Scoring Formula

In production clinical learning platforms, recommending topics requires balancing 4 signals:

$$\text{TopicScore}(t) = W_{\text{acc}} \cdot S_{\text{acc}}(t) + W_{\text{err}} \cdot S_{\text{err}}(t) + W_{\text{decay}} \cdot S_{\text{decay}}(t) + S_{\text{cold-start}}(t)$$

1. **Low Accuracy Signal ($S_{\text{acc}}$)**: Evaluates when accuracy is $< 50\%$. Reason: `"Low accuracy (33.3%)"`.

2. **Repeated Errors Signal ($S_{\text{err}}$)**: Triggered when incorrect attempts $\ge 3$. Reason: `"Repeated incorrect attempts (5 errors)"`.

3. **Time-Decay / Forgetting Curve ($S_{\text{decay}}$)**: Triggered when days since last review $\ge 14$ days. Reason: `"Long time since last review (18 days ago)"`.

4. **Cold Start Risk ($S_{\text{cold-start}}$)**: Assigns high priority ($85.0$) to unattempted topics. Reason: `"Unattempted topic — needs initial practice"`.

### Why This Explainable Algorithm Was Chosen

- **Real-Life Clinical Efficacy**: Mirrors spaced repetition learning systems (Anki / Duolingo).
- **Explainable Reasons**: Learners understand *why* a topic is prioritized.
- **Zero Inferencing Overhead**: Executes directly in < 5ms using database query aggregates.

---

## 5. ⚙️ Engineering Decisions & Trade-Offs

> 📖 **Full Engineering Decisions Review**: For complete senior engineering architectural justifications, see **[`ENGINEERING_DECISIONS.md`](./docs/ENGINEERING_DECISIONS.md)**.

### Key Technical Decisions & Strategy

1. **Database Design & Schema Isolation**: All entity tables scope within `learning_schema`. Many-to-Many junction tables enforce `ON DELETE CASCADE`, while MCQ options are stored in `jsonb` arrays to avoid `question_options` JOIN overhead.

2. **Modular Generic List Architecture**: Every repository inherits from `BaseRepository[T]`, delegating query building to `QueryBuilder` for reusable filtering, free-text ILIKE search, and type-safe `StrEnum` sorting (`QuestionSortField`, `TopicSortField`).

3. **Single Database Hit Window Count (`COUNT(*) OVER()`)**: Generic pagination attaches `COUNT(*) OVER()` window functions to fetch paginated entity slices and total unpaginated record counts in **1 database hit**, cutting database network roundtrips in half.

4. **Server-Side Derived Correctness**: Learner attempt submission payloads pass `selected_option_index`. Correctness (`is_correct`) is derived authoritatively on the server side to eliminate client score spoofing.

5. **What Was Intentionally Not Built**: Redis caching and asynchronous Kafka queues were omitted in Phase 1 to preserve transaction simplicity. Composite B-Tree indexes serve queries in < 5ms.

---

## 6. 🚀 Strategic Product Roadmap

> 📖 **Full CPO Product Review**: For complete feature impact analyses, clinical learning value justifications, and technical implementation feasibility, see **[`PRODUCT_ROADMAP.md`](./docs/PRODUCT_ROADMAP.md)**.

Evaluating a real-world medical clinical education platform with active daily learners, the following **5 realistic, feasible, and high-impact features** are recommended to drive learner retention and exam success:

1. **Metacognitive Confidence Ratings (`LOW`/`MEDIUM`/`HIGH`)**: Pinpoints overconfidence in incorrect answers ("unconscious incompetence"), the #1 cause of exam failure.

2. **Explanatory Distractor Breakdowns & "Clinical Pearls"**: Instant rationale feedback turning every attempt into an active learning moment.

3. **Dynamic Exam Readiness Index (0-100%)**: Weighted pass-prediction index alleviating medical student exam anxiety.

4. **Spaced Repetition Flashcard Export (Anki / Quizlet Sync)**: Direct `.apkg` deck export embedding Maxemo into medical students' daily study habit loop.

5. **Peer Cohort Percentile Benchmarking**: Cohort percentile ranks driving daily learner engagement.

---

## 7. 📅 Product Requirement Changes: 30-Day Exam Scenario

> 📖 **Full Technical Architecture**: For complete SQL table definitions, urgency weighting formulas, and Alembic rollout strategy, see **[`PRODUCT_REQUIREMENT_CHANGES.md`](./docs/PRODUCT_REQUIREMENT_CHANGES.md)**.

> **Scenario**: *"Learners preparing for an exam in the next 30 days should receive different recommendations from learners whose exam is six months away."*

### A. What Would Change?

Learners within 30 days of an exam need **High-Yield Exam Topic Weighting** and **Exam-Specific Revision Priorities** rather than general weak point practice.

### B. Would Database Schema Change?

**Yes.** We would introduce two new tables:
1. `user_exams`: Stores learner exam dates (`user_id`, `exam_name`, `exam_date`).
2. `exam_topic_weights`: Stores topic weight multipliers for specific exams (`exam_name`, `topic_id`, `weight_multiplier`).

### C. Would Recommendation Algorithm Change?

**Yes.** The ranking metric transitions to an **Urgency-Weighted Priority Score**.

### D. What Would Be Built First?

1. **Schema Migration**: Non-breaking Alembic migration adding `user_exams` table.
2. **Fallback Logic**: If no exam exists within 30 days, fall back to default topic accuracy ranking (zero breaking changes for existing users).

---

## 8. 📈 Scale Scenario: 10M Attempts Scaling Strategy

> 📖 **Full Scalability Architecture**: For complete throughput benchmarks, Redis caching sequence diagrams, and metric alerts, see **[`SCALABILITY.md`](./docs/SCALABILITY.md)**.

**Target Scale**: 100,000 active learners, 1,000,000 clinical questions, 10,000,000 question attempts.

### 4 Key System Bottlenecks & Production Remedies

| Identified Bottleneck | Cause / Symptom | Production Remedy |
|---|---|---|
| **1. DB Read Aggregation CPU Load** | Heavy `COUNT(*)` & `SUM(is_correct)` SQL queries on 10M+ rows for active performance dashboards | **Redis In-Memory Cache** (60s TTL) & **PostgreSQL Read Replicas** for read endpoints |
| **2. Write Lock Contention on Attempts** | High database disk write latency when thousands of learners submit attempts simultaneously | Async write streaming via **Kafka / RabbitMQ** message broker with batch consumer writes (500 records/chunk) |
| **3. Deep B-Tree Scans on Large Tables** | Linear B-Tree index depth increases on 10M+ rows, degrading lookup speeds | **Declarative Hash Partitioning** on `question_attempts` by `HASH(user_id)` across 16 database partitions |
| **4. Database Connection Starvation** | Concurrent client HTTP requests exhausting PostgreSQL maximum connection limits | Deploy **PgBouncer** connection pooler scaling up to 5,000+ active connections |

---

## 9. 🚀 Quick Start & Local Setup

### Prerequisites

- Python 3.12+
- `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- PostgreSQL 16 (or Docker Desktop)

```bash
# 1. Environment Setup
cp .env.example .env

# 2. Install Dependencies
uv sync

# 3. Spin up PostgreSQL
docker compose up -d postgres

# 4. Run Migrations
uv run alembic upgrade head

# 5. Seed Master Data (Topics & Questions)
uv run python -m scripts.seed_db

# 6. Seed Attempts (Optional)
uv run python -m scripts.seed_attempts --user-id 101 102 103

# 7. Start FastAPI Application
uv run uvicorn app.main:app --reload --port 8000
```

OpenAPI documentation is available at: **`http://localhost:8000/docs`**

---

## 10. 🐳 Docker Deployment

Deploy the entire production stack (FastAPI App + PostgreSQL + Automated Migrations) with one command:

```bash
docker compose up -d --build
```

- **Health Check Verification**:
  ```bash
  curl http://localhost:8000/health
  ```

---

## 11. 🧪 Testing & Quality Assurance

> 📖 **Full Testing Architecture**: For complete test isolation fixtures, mock session injection, and full 16-test suite catalog, see **[`TESTING.md`](./docs/TESTING.md)**.

The test suite covers unit level testing (domain services, mappers, exception logic) and end-to-end integration testing (repositories, API endpoints, database state transitions):

- **16 Integration & Unit Tests**: 100% passing test suite executing in **< 1.0 second**.
- **Transaction Isolation**: Tests run against isolated database transactions via `conftest.py` dependency overrides.
- **Strict Static Typing**: Passed under `mypy` strict static typing checks across all 62 source files.

```bash
# 1. Run Ruff Linter
uv run ruff check app/ scripts/ tests/

# 2. Run Mypy Static Type Checking
uv run mypy app/ scripts/

# 3. Run Pytest Integration Test Suite
uv run pytest tests/ -v
```

All 16 integration and unit tests pass cleanly in **< 1.0 second**.

---

## 12. 📜 Architectural Decision Records (ADRs)

> 📖 **Full Decision Records Log**: For complete rationale, considered options, pros/cons, and trade-offs of all 8 formal architectural decisions, see **[`DECISIONS.md`](./docs/DECISIONS.md)**.

Formal decision records documented in the project repository:

- **ADR-001**: Choice of Clean Architecture Layered Structure (`app/api`, `app/service`, `app/repository`)
- **ADR-002**: Generic Repository Pattern (`BaseRepository[T]`) & Dynamic `QueryBuilder`
- **ADR-003**: Hybrid Primary Key Strategy (UUID v4 for public entities, BigInt for user IDs)
- **ADR-004**: Server-Side Derived Option Correctness (`is_correct` computed authoritatively on server)
- **ADR-005**: Stateless Dynamic Performance Calculation (aggregates computed via DB query)
- **ADR-006**: Omission of Redis Cache in Phase 1 (relying on PostgreSQL B-Tree indexes)
- **ADR-007**: Omission of Asynchronous Message Queues in Phase 1 (direct DB write for instant feedback)
- **ADR-008**: Window Function (`COUNT(*) OVER()`) Single-Query Pagination

---

## 13. 🤖 AI Tools Used

This project was developed with assistance from **Antigravity AI**:

- **Code Generation & Boilerplate Setup**: Scaffolding SQLAlchemy 2.0 models, Alembic async migration environment, and Pydantic schemas.
- **Test Suite Generation**: Writing comprehensive Pytest async unit and API integration tests.
- **Documentation Architecture**: Generating structured markdown technical documentation.
