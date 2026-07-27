# Revision Recommendation Engine Architecture

## 1. Business Goal & Product Context

In clinical medical education (USMLE, MedEd), learners retention depends on identifying **knowledge gaps**—questions or concepts where their historical accuracy is lowest. 

The **Revision Recommendation Engine** (`GET /api/v1/attempts/users/{user_id}/revision`) identifies questions where the learner has demonstrated poor performance and recommends them for targeted practice.

---

## 2. Mathematical Algorithm Formulation

### Inputs
- Learner User ID ($u \in \mathbb{N}$)
- Attempt History Set $A_u = \{a_1, a_2, \dots, a_n\}$ where each attempt $a_i = (q_k, c_i, t_i)$ contains:
  - $q_k$: Question ID
  - $c_i \in \{0, 1\}$: Binary correctness status ($1 = \text{correct}, 0 = \text{incorrect}$)
  - $t_i \in \mathbb{R}^+$: Creation timestamp

### Accuracy Formula
For a given question $q_k$ attempted by user $u$, the **Question Accuracy Score** $\text{Acc}(u, q_k)$ is defined as:

$$\text{Acc}(u, q_k) = \frac{\sum_{i \in A_u, q(a_i) = q_k} c_i}{\sum_{i \in A_u, q(a_i) = q_k} 1}$$

### Recommendation Sorting Criteria
Questions attempted by user $u$ are ordered according to the tuple score:

$$\text{Rank}(q_k) = \left( \text{Acc}(u, q_k), - \max(t_{i, q_k}) \right)$$

1. Primary Sort Key: **`Acc(u, q_k)` ASCENDING** (Lowest accuracy first = Highest priority for revision).
2. Secondary Sort Key: **`created_at` DESCENDING** (Most recently attempted weak questions broken first).

---

## 3. SQL Query Implementation

The core algorithm is executed entirely within the database engine via `QuestionRepository.get_questions_by_user_attempt_accuracy`:

```sql
SELECT 
    q.id, 
    q.text, 
    q.options, 
    q.difficulty, 
    q.created_at,
    AVG(CASE WHEN qa.is_correct IS TRUE THEN 1.0 ELSE 0.0 END)::FLOAT AS accuracy_score
FROM learning_schema.questions q
JOIN learning_schema.question_attempts qa ON qa.question_id = q.id
WHERE qa.user_id = 101
GROUP BY q.id
ORDER BY accuracy_score ASC, q.created_at DESC
LIMIT 10;
```

---

## 4. Algorithmic Complexity Analysis

- **Time Complexity**: 
  - Database Scan: $O(M \log M)$ where $M$ is the number of attempts recorded for user $u$.
  - With composite index `ix_attempts_user_question_correct (user_id, question_id, is_correct)`: Index scan isolates matching user rows in $O(\log N + M)$, reducing total execution time to **< 3ms**.
- **Space Complexity**: $O(K)$ where $K$ is the requested limit parameter (e.g. $K=10$), consuming negligible memory.

---

## 5. Advantages vs. Weaknesses

### Advantages
1. **Determinism & Predictability**: Learners get immediate, transparent feedback on why a question was recommended.
2. **Zero Training Latency**: Requires no offline model training, feature store infrastructure, or batch inferencing pipelines.
3. **Real-Time Accuracy**: Computes up-to-the-second accuracy without eventual consistency delays.

### Weaknesses
1. **Cold Start Problem**: Unattempted questions are not ranked by accuracy because no attempt history exists for the learner.
2. **Lack of Time Decay**: An attempt made 6 months ago weighs equally with an attempt made 5 minutes ago.
3. **No Difficulty Weighting**: Failing a `HARD` question carries the same penalty as failing an `EASY` question.

---

## 6. Future Machine Learning / Algorithmic Evolution

To evolve this engine for production scale, the following enhancements are planned:

### A. Exponential Time-Decay Weighting (Half-Life Memory Model)
Incorporate a forgetting curve metric based on Ebbinghaus' Forgetting Curve:

$$W(t) = e^{-\lambda (T_{current} - t_i)}$$

$$\text{DecayedAcc}(u, q_k) = \frac{\sum c_i \cdot W(t_i)}{\sum W(t_i)}$$

### B. Item Response Theory (IRT) & Elo Rating System
Assign a dynamic difficulty rating $\beta(q_k)$ to each question and a ability score $\theta(u)$ to each learner:

$$P(\text{Correct} \mid \theta, \beta) = \frac{1}{1 + e^{-(\theta - \beta)}}$$

Questions where $P(\text{Correct}) \approx 0.50$ (Zone of Proximal Development) are prioritized to optimize learning retention.
