# 🔌 API Design Specification & OpenAPI Standard

## Executive Summary

The API presentation layer is built following **RESTful standards**, returning standardized JSON envelopes for all success and error responses. 

OpenAPI 3.1 documentation is generated automatically at `/docs`.

---

## 1. 📦 Global Response Envelope Format

All endpoints wrap their JSON payloads in a uniform response envelope (`APIResponse[T]` defined in `app/schema/response.py`).

### Success Response Envelope (`200 OK`, `201 Created`)

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "error": null
}
```

### Error Response Envelope (`400`, `404`, `409`, `500`)

```json
{
  "success": false,
  "message": "Question with ID 'e8f4362e-66e4-427f-a18e-4e29b8affac3' was not found.",
  "data": null,
  "error": {
    "code": "QUESTION_NOT_FOUND",
    "message": "Question with ID 'e8f4362e-66e4-427f-a18e-4e29b8affac3' was not found.",
    "details": null
  }
}
```

---

## 2. 🚦 HTTP Status Code Conventions

| HTTP Status Code | Scenario |
|---|---|
| **`200 OK`** | Successful retrieval, update, deletion, or query calculation |
| **`201 Created`** | Successful resource creation (`POST /topics`, `POST /questions`, `POST /attempts`) |
| **`400 Bad Request`** | Validation failure (e.g. invalid option index out of range) |
| **`404 Not Found`** | Requested topic or question UUID does not exist |
| **`409 Conflict`** | Duplicate creation attempt (e.g. creating topic with existing name) |
| **`500 Internal Error`** | Unhandled exception (caught by global exception handler) |

---

## 3. 🛠️ Detailed Endpoint Specifications

### A. Health Check API

#### `GET /health` (Unversioned Root Endpoint)

- **Summary**: Microservice health and status check.
- **Response `200 OK`**:
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

### B. Topics API (`/api/v1/topics`)

#### `POST /api/v1/topics`

- **Summary**: Create a new learning topic (e.g., *Cardiology*, *Renal Pathology*).
- **Request Body (`TopicCreate`)**:
  ```json
  {
    "name": "Cardiology"
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "success": true,
    "message": "Topic created successfully",
    "data": {
      "id": "3a8fc094-f3db-4534-a71c-10c2c628a012",
      "name": "Cardiology",
      "created_at": "2026-07-27T14:00:00Z",
      "updated_at": "2026-07-27T14:00:00Z"
    },
    "error": null
  }
  ```
- **Error Response `409 Conflict`**: If topic with exact name already exists (`TOPIC_ALREADY_EXISTS`).

#### `GET /api/v1/topics`

- **Summary**: List topics with single-query window count (`COUNT(*) OVER()`), filtering, search, and type-safe sorting.
- **Query Parameters**:
  - `offset` (int, default: 0)
  - `limit` (int, default: 20)
  - `search` (string, optional): Free-text search on topic name
  - `sort_by` (enum: `name`, `created_at`, default: `created_at`)
  - `sort_order` (enum: `asc`, `desc`, default: `desc`)

---

### C. Questions API (`/api/v1/questions`)

#### `POST /api/v1/questions`

- **Summary**: Create a new clinical multiple-choice question.
- **Request Body (`QuestionCreate`)**:
  ```json
  {
    "text": "Which drug is a first-line rate control agent for atrial fibrillation?",
    "options": ["Amiodarone", "Diltiazem", "Digoxin", "Atropine"],
    "correct_option_index": 1,
    "difficulty": "easy",
    "topic_ids": ["3a8fc094-f3db-4534-a71c-10c2c628a012"]
  }
  ```
- **Validation Rules**: `correct_option_index` must be within `0 <= index < len(options)`.

#### `GET /api/v1/questions/{question_id}` (Learner View)

- **Security Rule**: Excludes `correct_option_index` from payload to prevent client-side answer cheating.
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "Question retrieved successfully",
    "data": {
      "id": "e8f4362e-66e4-427f-a18e-4e29b8affac3",
      "text": "Which drug is a first-line rate control agent for atrial fibrillation?",
      "options": ["Amiodarone", "Diltiazem", "Digoxin", "Atropine"],
      "difficulty": "easy",
      "topics": [{ "id": "3a8fc094-f3db-4534-a71c-10c2c628a012", "name": "Cardiology" }],
      "created_at": "2026-07-27T14:00:00Z",
      "updated_at": "2026-07-27T14:00:00Z"
    },
    "error": null
  }
  ```

#### `GET /api/v1/questions/practice` (Practice Mode)

- **Query Parameters**:
  - `topic_ids` (list of UUIDs): Filter practice questions by topics.
  - `limit` (int, default: 10): Number of practice questions to fetch.

---

### D. Attempts & Analytics API (`/api/v1/attempts`, `/api/v1/users`)

#### `POST /api/v1/attempts`

- **Summary**: Record a learner's question attempt.
- **Server-Side Derived Correctness**: Payload contains `selected_option_index` and `time_taken_seconds`. Server compares `selected_option_index == question.correct_option_index` to compute `is_correct`, eliminating client-side score spoofing.
- **Request Body (`AttemptSubmit`)**:
  ```json
  {
    "user_id": 101,
    "question_id": "e8f4362e-66e4-427f-a18e-4e29b8affac3",
    "selected_option_index": 1,
    "time_taken_seconds": 15
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "success": true,
    "message": "Attempt recorded successfully",
    "data": {
      "id": "7049c864-58c1-4b66-acb3-a15c190aff8e",
      "user_id": 101,
      "question_id": "e8f4362e-66e4-427f-a18e-4e29b8affac3",
      "selected_option_index": 1,
      "is_correct": true,
      "time_taken_seconds": 15,
      "created_at": "2026-07-27T14:05:00Z"
    },
    "error": null
  }
  ```

---

#### `GET /api/v1/users/{user_id}/performance`

- **Summary**: Get learner performance summary and per-topic breakdown calculated dynamically via database query aggregates.
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "User performance calculated successfully",
    "data": {
      "user_id": 101,
      "total_attempts": 32,
      "correct_attempts": 20,
      "accuracy_percentage": 62.5,
      "avg_time_taken_seconds": 45.2,
      "topic_breakdown": [
        {
          "topic_id": "3a8fc094-f3db-4534-a71c-10c2c628a012",
          "topic_name": "Cardiology",
          "total_attempts": 20,
          "correct_attempts": 16,
          "accuracy_percentage": 80.0
        },
        {
          "topic_id": "fae8489d-5a66-4723-88f8-0e2575634e40",
          "topic_name": "Renal Pathology",
          "total_attempts": 12,
          "correct_attempts": 4,
          "accuracy_percentage": 33.3
        }
      ]
    },
    "error": null
  }
  ```

---

#### `GET /api/v1/users/{user_id}/revision`

- **Summary**: Get personalized topic revision queue (recommends top ~5 weak topics to revise next with priority ranks and explainable human reasons).
- **Query Parameters**: `limit` (int, default: 5)
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "Topic revision queue calculated successfully",
    "data": {
      "user_id": 101,
      "recommendations": [
        {
          "topic_id": "fae8489d-5a66-4723-88f8-0e2575634e40",
          "topic": "Renal Pathology",
          "priority": 1,
          "reason": "Low accuracy (33.3%)",
          "accuracy_percentage": 33.3,
          "total_attempts": 12,
          "correct_attempts": 4,
          "last_attempted_at": "2026-07-27T10:00:00Z"
        },
        {
          "topic_id": "00ab295b-7ac3-4ce2-97e2-5776ec66a38e",
          "topic": "Microbiology",
          "priority": 2,
          "reason": "Repeated incorrect attempts (5 errors)",
          "accuracy_percentage": 40.0,
          "total_attempts": 10,
          "correct_attempts": 4,
          "last_attempted_at": "2026-07-26T15:30:00Z"
        }
      ]
    },
    "error": null
  }
  ```

---

#### `GET /api/v1/users/{user_id}/revision/questions`

- **Summary**: Get specific weak questions recommended for targeted practice based on historical learner accuracy.
- **Query Parameters**: `limit` (int, default: 10)

---

#### `GET /api/v1/users/{user_id}/attempts`

- **Summary**: List a learner's historical attempts with pagination.
- **Query Parameters**: `offset` (default: 0), `limit` (default: 20), `sort_by` (`created_at`), `sort_order` (`asc`/`desc`).
