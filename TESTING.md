# Testing Strategy & Automated Test Suite Documentation

## Executive Summary

The microservice includes a comprehensive test suite using **Pytest** and **Pytest-Asyncio** (`asyncio_mode = "auto"`). Tests cover unit level testing (services, mappers, exception logic) and full end-to-end integration testing (repositories, API endpoints, database state transitions).

---

## 1. Test Suite Architecture

```
tests/
├── __init__.py           # Package marker
├── conftest.py           # Pytest async session fixtures & dependency overrides
├── test_api.py           # End-to-End FastAPI integration tests
├── test_exceptions.py    # Custom & Unhandled exception handler tests
├── test_health.py        # Health check endpoint tests
├── test_repositories.py  # Data access repository CRUD tests
└── test_services.py      # Business logic unit & integration tests
```

---

## 2. Test Execution & Coverage Command

To execute the test suite locally or in CI/CD pipelines:

```bash
# Run all tests with verbose output
uv run pytest tests/ -v

# Run with test coverage reporting
uv run pytest --cov=app tests/ --cov-report=term-missing
```

---

## 3. Test Isolation & Dependency Overriding

In `tests/conftest.py`, the production database session factory is overridden using FastAPI's `app.dependency_overrides` mechanism:

```python
# tests/conftest.py
@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    application = create_app()
    
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    application.dependency_overrides[get_db_session] = _get_test_db
    return application
```

- Each test function executes inside an isolated database session.
- Dynamic entity names with unique hex suffixes (e.g. `f"Pulmonology-{uuid.uuid4().hex[:6]}"`) prevent database key collisions when running against persistent test databases.

---

## 4. Test Catalog & Edge Cases Tested

### A. Repositories Tests (`tests/test_repositories.py`)
- `test_topic_repository_crud`: Validates creation, `get_by_id`, `get_by_name`, and paginated list queries.
- `test_question_repository_crud`: Validates question creation with relationship join to topics, relationship eager loading via `selectinload`, topic filtering, and cascade deletion.
- `test_attempt_repository_raw_queries`: Asserts DB raw aggregate calculation (`total_attempts`, `correct_attempts`, `total_time_seconds`).

### B. Service Unit Tests (`tests/test_services.py`)
- `test_topic_service_create_and_duplicate`: Verifies `TopicAlreadyExistsException` is raised on duplicate names.
- `test_question_service_create_and_option_validation`: Asserts `InvalidOptionIndexException` is raised when `correct_option_index >= len(options)`.
- `test_attempt_service_server_derived_correctness`: Verifies server enforces `is_correct = (selected_option_index == correct_option_index)` regardless of client input.

### C. API End-to-End Tests (`tests/test_api.py`)
- `test_topics_api_flow`: Complete lifecycle: POST topic -> duplicate POST -> GET topic -> GET list paginated.
- `test_questions_and_attempts_api_flow`: Full vertical slice: POST topic -> POST question -> GET learner view (asserts `correct_option_index` excluded) -> POST attempt -> GET performance -> GET revision recommendations.

### D. Exception Handler Tests (`tests/test_exceptions.py`)
- `test_custom_exception_returns_formatted_json`: Asserts custom domain exceptions format structured `APIResponse` with HTTP 404/400/409 codes.
- `test_unhandled_exception_returns_500_internal_server_error`: Asserts unhandled system crashes return HTTP 500 without leaking sensitive tracebacks to clients.

---

## 5. Performance & Regression Standards

1. **Test Suite Latency**: The complete 15-test suite executes in **< 1.0 second**.
2. **Ruff & Mypy Strict Compliance**: All tests pass `ruff check` and `mypy` strict static typing checks.
