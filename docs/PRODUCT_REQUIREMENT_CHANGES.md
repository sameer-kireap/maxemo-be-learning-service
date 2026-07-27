# Product Requirement Changes Architecture: 30-Day Exam Scenario

## Executive Overview

This document details the architectural impact, database schema additions, mathematical algorithm adjustments, and migration strategy required to adapt the Maxemo Learning Analytics Service to the following evolving product requirement:

> **Product Requirement Change**: *"Learners preparing for an exam in the next 30 days should receive different recommendations from learners whose exam is six months away."*

---

## 1. Scenario & Product Analysis

When an exam is $\le 30$ days away, learner behavior and pedagogical needs shift:
- **General Weak Point Practice $\rightarrow$ High-Yield Exam Focus**: Learners can no longer afford to review all historical weak topics broadly. The recommendation engine must prioritize topics heavily weighted on their specific upcoming exam.
- **Urgency Time-Decay Weighting**: Topics with low accuracy on high-yield exam categories must receive massive priority multipliers as $\text{DaysToExam} \to 0$.

---

## 2. Database Schema Changes

To support learner exam schedules and exam-topic high-yield weightings, two new tables are introduced into `learning_schema`:

```sql
-- 1. Learner Exam Schedules
CREATE TABLE learning_schema.user_exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    exam_name VARCHAR(255) NOT NULL,
    exam_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast user exam lookup and date filtering
CREATE INDEX ix_user_exams_user_date ON learning_schema.user_exams (user_id, exam_date);

-- 2. Exam Topic High-Yield Weightings
CREATE TABLE learning_schema.exam_topic_weights (
    exam_name VARCHAR(255) NOT NULL,
    topic_id UUID NOT NULL REFERENCES learning_schema.topics(id) ON DELETE CASCADE,
    weight_multiplier FLOAT NOT NULL DEFAULT 1.0,
    is_high_yield BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (exam_name, topic_id)
);
```

### Table Definitions & Purpose:
- **`user_exams`**: Tracks when a learner is taking a specific board or clinical exam (e.g. *USMLE Step 1* on *2026-08-25*).
- **`exam_topic_weights`**: Maps high-yield multipliers per exam topic (e.g. *Cardiology* has a $2.0\times$ weight for USMLE Step 1).

---

## 3. Mathematical Scoring Algorithm Changes

The topic priority scoring algorithm transitions from pure accuracy ranking to an **Urgency-Weighted Priority Score**:

$$\text{DaysToExam} = \max\left(1, \lfloor \text{exam-date} - \text{current-date} \rfloor\right)$$

$$\text{UrgencyWeight}(\text{DaysToExam}) = \begin{cases} 
2.5 & \text{if } \text{DaysToExam} \le 14 \text{ (Sprint Revision)} \\
1.8 & \text{if } 14 < \text{DaysToExam} \le 30 \text{ (High-Yield Focus)} \\
1.0 & \text{if } \text{DaysToExam} > 30 \text{ (General Practice)}
\end{cases}$$

$$\text{PriorityScore}(u, t) = \left(100.0 - \text{Accuracy}(u, t)\right) \times \text{UrgencyWeight} \times \text{WeightMultiplier}(t)$$

Topics with the **highest `PriorityScore`** are recommended first.

---

## 4. Phased Implementation Roadmap & Priorities

To deliver this feature safely in production without disrupting active learners:

### Phase 1: Non-Breaking Database Migration
1. Execute an Alembic migration creating `user_exams` and `exam_topic_weights`.
2. Seed default exam high-yield topic weights.

### Phase 2: Fallback Logic & Zero Breaking Changes
1. If `user_exams` query returns no exam within 30 days for a learner, the service automatically falls back to the default accuracy recommendation engine.

### Phase 3: Feature Flag Rollout
1. Enable exam-weighted recommendations behind a feature flag (`ENABLE_EXAM_DRIVEN_REVISION=true`).
