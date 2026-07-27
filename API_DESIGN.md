# API Design Specification & OpenAPI Standard

## Executive Summary

The API presentation layer is built following **RESTful standards**, returning standardized JSON envelopes for all success and error responses. OpenAPI 3.1 documentation is generated automatically at `/docs`.

---

## 1. Global Response Envelope Format

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

## 2. HTTP Status Code Conventions

| HTTP Status Code | Scenario |
|---|---|
| **`200 OK`** | Successful retrieval, update, deletion, or query calculation |
| **`201 Created`** | Successful resource creation (`POST /topics`, `POST /questions`, `POST /attempts`) |
| **`400 Bad Request`** | Validation failure (e.g. invalid option index out of range) |
| **`404 Not Found`** | Requested topic or question UUID does not exist |
| **`409 Conflict`** | Duplicate creation attempt (e.g. creating topic with existing name) |
| **`500 Internal Error`** | Unhandled exception (caught by global exception handler) |

---

## 3. Detailed Endpoint Specifications

### A. Health Check
- **`GET /health`** (Unversioned Root Endpoint)
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

#### `GET /api/v1/topics`
- **Query Parameters**:
  - `offset` (int, default: 0)
  - `limit` (int, default: 20)
  - `search` (string, optional): Free-text search on topic name
  - `sort_by` (enum: `name`, `created_at`): Type-safe sort field
  - `sort_order` (enum: `asc`, `desc`, default: `desc`)

---

### C. Questions API (`/api/v1/questions`)

#### `POST /api/v1/questions`
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

---

### D. Attempts & Analytics API (`/api/v1/attempts`)

#### `POST /api/v1/attempts`
- **Request Body (`AttemptSubmit`)**:
  ```json
  {
    "user_id": 101,
    "question_id": "e8f4362e-66e4-427f-a18e-4e29b8affac3",
    "selected_option_index": 1,
    "time_taken_seconds": 15
  }
  ```
- **Response `201 Created`** (Server-derived `is_correct`):
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

#### `GET /api/v1/attempts/users/{user_id}/performance`
- **Response `200 OK`**:
  ```json
  {
    "success": true,
    "message": "User performance calculated successfully",
    "data": {
      "user_id": 101,
      "total_attempts": 10,
      "correct_attempts": 8,
      "accuracy_percentage": 80.0,
      "avg_time_taken_seconds": 14.5,
      "topic_breakdown": [
        {
          "topic_id": "3a8fc094-f3db-4534-a71c-10c2c628a012",
          "topic_name": "Cardiology",
          "total_attempts": 5,
          "correct_attempts": 4,
          "accuracy_percentage": 80.0
        }
      ]
    },
    "error": null
  }
  ```
