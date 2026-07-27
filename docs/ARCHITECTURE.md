# Architecture & System Design Documentation

## Executive Overview

The **Maxemo Learning Analytics Service** is constructed using **Clean Architecture** principles adapted for modern Python 3.12 microservices. The core philosophy is **strict separation of concerns**, **unidirectional dependency flow** (inner domain layers know nothing about outer HTTP/database layers), and **inversion of control (IoC)** via FastAPI dependency injection.

---

## 1. Clean Architecture Layers

```mermaid
graph TD
    subgraph Presentation Layer ["Presentation Layer (app/api/)"]
        A[FastAPI Routers] --> B[Pydantic Request/Response DTOs]
    end

    subgraph Service & Interface Layer ["Service & Interface Layer (app/service/, app/interface/)"]
        C[Abstract Service Interfaces - ABC] --> D[Domain Service Implementations]
        D --> E[Custom Domain Exceptions]
        D --> F[DTO Mappers]
    end

    subgraph Repository Layer ["Repository Layer (app/repository/, app/utils/)"]
        G[BaseRepository - Generic] --> H[QueryBuilder - Window Count]
        H --> I[Concrete Repositories - Topic, Question, Attempt]
    end

    subgraph Database Infrastructure Layer ["Database Infrastructure Layer (app/core/, app/model/)"]
        J[Async SQLAlchemy Engine] --> K[PostgreSQL 16 - learning_schema]
    end

    Presentation Layer --> Service & Interface Layer
    Service & Interface Layer --> Repository Layer
    Repository Layer --> Database Infrastructure Layer
```

### Layer Breakdown

#### A. Presentation Layer (`app/api/v1/`, `app/api/health.py`)
- **Responsibility**: HTTP request parsing, query parameter validation, routing, HTTP status code response formatting, and OpenAPI schema generation.
- **Rules**:
  - Routers contain **zero business logic**.
  - Handlers accept Pydantic DTOs and injected Service Interfaces via `Depends()`.
  - All responses are wrapped in standard `APIResponse[T]` or `APIResponse[PaginatedResponse[T]]`.

#### B. Service & Domain Layer (`app/service/`, `app/interface/`, `app/mapper/`, `app/exception/`)
- **Responsibility**: Business rules, invariants, validation logic, entity transformations, scoring calculations, and orchestrating repositories.
- **Rules**:
  - Services inherit from abstract base classes (`ITopicService`, `IQuestionService`, `IAttemptService`).
  - Services accept and return Pydantic DTO objects directly.
  - Exception triggers raise domain-specific exceptions (`QuestionNotFoundException`, `InvalidOptionIndexException`).

#### C. Data Access & Repository Layer (`app/repository/`, `app/utils/repository/`)
- **Responsibility**: Constructing type-safe SQLAlchemy queries, executing database calls, handling pagination/filtering/sorting, and fetching raw DB aggregate tuples.
- **Rules**:
  - Repositories perform **pure data access only**. They do not calculate percentages or mutate business states.
  - Implement single-query `COUNT(*) OVER()` window count pagination via `BaseRepository.list_generic`.

#### D. Infrastructure Layer (`app/core/`, `app/model/`)
- **Responsibility**: DB connection pool management (`asyncpg`), environment configuration (`pydantic-settings`), logging configuration, and ORM entity declarations (`app/model/`).

---

## 2. Request & Execution Lifecycle

The sequence diagram below traces an incoming HTTP submission (`POST /api/v1/attempts`) through all layers of the system:

```mermaid
sequenceDiagram
    autonumber
    participant Client as HTTP Client
    participant Router as Attempts Router (app/api/v1/attempts.py)
    participant DI as Dependency Injector (app/dependencies/attempt.py)
    participant Service as AttemptService (app/service/attempt_service.py)
    participant QRepo as QuestionRepository (app/repository/question_repository.py)
    participant ARepo as AttemptRepository (app/repository/attempt_repository.py)
    participant DB as PostgreSQL Database

    Client->>Router: POST /api/v1/attempts (AttemptSubmit JSON)
    Router->>DI: Resolve get_attempt_service()
    DI->>Service: Inject AttemptRepository & QuestionRepository
    Router->>Service: submit_attempt(payload: AttemptSubmit)
    
    Service->>QRepo: get_by_id(payload.question_id)
    QRepo->>DB: SELECT * FROM learning_schema.questions WHERE id = $1
    DB-->>QRepo: Question ORM Entity (with options & correct_option_index)
    QRepo-->>Service: Return Question ORM object

    alt Question Not Found
        Service-->>Router: raise QuestionNotFoundException(question_id)
        Router-->>Client: 404 Not Found (APIResponse error payload)
    end

    Note over Service: Enforce Business Invariant:<br/>is_correct = (selected_option_index == question.correct_option_index)
    
    Service->>Service: AttemptMapper.to_entity(payload, is_correct)
    Service->>ARepo: create(QuestionAttempt ORM Entity)
    ARepo->>DB: INSERT INTO learning_schema.question_attempts ...
    DB-->>ARepo: Created Record
    ARepo-->>Service: Return QuestionAttempt Entity

    Service->>Service: AttemptMapper.to_response(created_attempt)
    Service-->>Router: Return AttemptResponse DTO
    Router-->>Client: 201 Created (APIResponse[AttemptResponse])
```

---

## 3. Dependency Flow & Modular Inversion of Control

To avoid **circular imports** in Python microservices, dependencies are organized into domain-isolated modules under `app/dependencies/`:

```
app/dependencies/
├── __init__.py       # Re-exports all dependency factories
├── database.py       # AsyncSession generator (get_db_session)
├── topic.py          # get_topic_repository, get_topic_service
├── question.py       # get_question_repository, get_question_service
└── attempt.py        # get_attempt_repository, get_attempt_service
```

### Injection Flow
1. FastAPI resolves `get_attempt_service(db: AsyncSession = Depends(get_db_session))`.
2. `get_attempt_service` instantiates concrete `AttemptRepository(db)` and `QuestionRepository(db)`.
3. `AttemptService` is instantiated with these repository instances and returned as `IAttemptService`.

---

## 4. Error & Exception Handling Architecture

The application enforces a centralized, 3-pronged exception handling system registered in `app/exception/handler.py`. All domain exceptions derive from `CustomException` (`app/exception/base.py`), ensuring standard error payloads without leaking raw internal stack traces.

```mermaid
graph TD
    A[Exception Raised During Request Execution] --> B{Exception Type}
    
    B -- Custom Domain Exception --> C[custom_exception_handler]
    B -- Request Validation Error --> D[validation_exception_handler]
    B -- Unhandled System Crash --> E[global_unhandled_exception_handler]
    
    C --> F["Extract status_code (HTTP 400 / 404 / 409)<br/>Read custom error_code & message"]
    D --> G["Extract Pydantic field location & validation rule<br/>Return HTTP 422 UNPROCESSABLE_ENTITY"]
    E --> H["Log full traceback via logger.exception<br/>Return HTTP 500 INTERNAL_SERVER_ERROR"]
    
    F --> I["Format Unified Error Payload<br/>{'error': {'code': ..., 'message': ..., 'details': ...}}"]
    G --> I
    H --> I
    
    I --> J[Return JSONResponse to Client]
```

### Exception Class Taxonomy & Mappings

| Exception Class | Parent Class | Status Code | Error Code | Description / Trigger |
|---|---|---|---|---|
| **`TopicNotFoundException`** | `CustomException` | `404 NOT FOUND` | `TOPIC_NOT_FOUND` | Raised when requested Topic UUID does not exist |
| **`QuestionNotFoundException`** | `CustomException` | `404 NOT FOUND` | `QUESTION_NOT_FOUND` | Raised when requested Question UUID does not exist |
| **`TopicAlreadyExistsException`** | `CustomException` | `409 CONFLICT` | `TOPIC_ALREADY_EXISTS` | Raised when creating a Topic with a duplicate name |
| **`InvalidOptionIndexException`** | `CustomException` | `400 BAD REQUEST` | `INVALID_OPTION_INDEX` | Raised when `correct_option_index` or `selected_option_index` is out of bounds |
| **`RequestValidationError`** | FastAPI / Pydantic | `422 UNPROCESSABLE` | `VALIDATION_ERROR` | Raised automatically on payload schema/type mismatch |
| **`Unhandled Exception`** | `Exception` | `500 INTERNAL ERROR` | `INTERNAL_SERVER_ERROR` | Catch-all for uncaught system bugs (logs traceback safely) |


---

## 5. Configuration & Environment Management

Configuration management is powered by `pydantic-settings` in `app/core/config.py`:
- Reads environment variables from system env or `.env` file.
- Enforces strict validation of DB connection strings, log levels, and application metadata.
- Leverages `@lru_cache` on `get_settings()` to avoid reading `.env` on every request.

---

## 6. Architectural Trade-Offs & Scaling Analysis

| Decision | Pros | Cons | Mitigation / Evolution |
|---|---|---|---|
| **Stateless Performance Calculations** | No state sync bugs; accurate real-time aggregates | Higher DB CPU load on massive attempt tables | Composite indexes `(user_id, question_id)` + Read Replicas |
| **Monolithic Microservice Service Structure** | High cohesion, zero network latency between components | All endpoints share process memory | Separate into read/write microservices if RPS exceeds 50,000 |
| **Generic List Window Query** | 1 DB roundtrip for items + total count | Window count can be slow on 10M+ rows without indexes | Add index-covered filter columns or table partitioning |
