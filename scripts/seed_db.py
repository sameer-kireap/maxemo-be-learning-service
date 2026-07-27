"""Database seeder script for populating master data (Topics and Questions)."""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constant.difficulty import DifficultyLevel
from app.core.config import get_settings
from app.core.database import get_session_factory
from app.core.logger import setup_logging
from app.model.question import Question
from app.model.topic import Topic

logger = logging.getLogger(__name__)

TOPICS_DATA = [
    "Cardiology",
    "Neurology",
    "Pulmonology",
    "Endocrinology",
    "Gastroenterology",
    "Pharmacology",
]

QUESTIONS_DATA: list[dict[str, object]] = [
    {
        "topic": "Cardiology",
        "text": (
            "A 65-year-old male presents with crushing substernal chest pain "
            "radiating to the left arm. ECG shows ST-segment elevation in leads II, III, and aVF. "
            "Which coronary artery is most likely occluded?"
        ),
        "options": [
            "Left Anterior Descending (LAD)",
            "Right Coronary Artery (RCA)",
            "Left Circumflex Artery (LCx)",
            "Left Main Coronary Artery",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.MEDIUM,
    },
    {
        "topic": "Cardiology",
        "text": (
            "Which drug is a first-line rate control agent for atrial fibrillation "
            "in patients without heart failure?"
        ),
        "options": ["Amiodarone", "Diltiazem", "Digoxin", "Atropine"],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Cardiology",
        "text": "Which heart sound is classically associated with severe mitral stenosis?",
        "options": [
            "S3 Gallop",
            "S4 Gallop",
            "Opening Snap followed by diastolic rumble",
            "Mid-systolic click",
        ],
        "correct_option_index": 2,
        "difficulty": DifficultyLevel.HARD,
    },
    {
        "topic": "Neurology",
        "text": (
            "A 45-year-old female presents with sudden onset weakness of the right face and arm, "
            "and motor aphasia. Which vascular territory is affected?"
        ),
        "options": [
            "Left Anterior Cerebral Artery (ACA)",
            "Left Middle Cerebral Artery (MCA) superior division",
            "Right Middle Cerebral Artery (MCA)",
            "Posterior Inferior Cerebellar Artery (PICA)",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.MEDIUM,
    },
    {
        "topic": "Neurology",
        "text": (
            "What is the hallmark histopathological feature of Parkinson's disease "
            "found in the substantia nigra?"
        ),
        "options": [
            "Amyloid Plaques",
            "Neurofibrillary Tangles",
            "Lewy Bodies (alpha-synuclein aggregates)",
            "Pick Bodies",
        ],
        "correct_option_index": 2,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Pulmonology",
        "text": (
            "A 24-year-old tall, thin male experiences sudden right-sided chest pain "
            "and shortness of breath while playing basketball. Trachea is midline. "
            "What is the most likely diagnosis?"
        ),
        "options": [
            "Tension Pneumothorax",
            "Primary Spontaneous Pneumothorax",
            "Pulmonary Embolism",
            "Aortic Dissection",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Pulmonology",
        "text": (
            "Which arterial blood gas pattern is expected in acute hyperventilating "
            "asthma exacerbation prior to fatigue?"
        ),
        "options": [
            "Respiratory Acidosis",
            "Respiratory Alkalosis with Hypocapnia",
            "Metabolic Acidosis",
            "Normal ABG",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.MEDIUM,
    },
    {
        "topic": "Endocrinology",
        "text": (
            "A 35-year-old female presents with weight loss, heat intolerance, tremor, "
            "and exophthalmos. TSH is undetectable and free T4 is elevated. "
            "What is the most common cause?"
        ),
        "options": [
            "Hashimoto Thyroiditis",
            "Graves' Disease",
            "Subacute Granulomatous Thyroiditis",
            "Toxic Multinodular Goiter",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Endocrinology",
        "text": (
            "Which lab finding distinguishes Primary Adrenal Insufficiency (Addison's) "
            "from Secondary Adrenal Insufficiency?"
        ),
        "options": [
            "Low Morning Cortisol",
            "Elevated Plasma ACTH and Hyperpigmentation",
            "Low Plasma Aldosterone in Secondary",
            "Hyperglycemia",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.HARD,
    },
    {
        "topic": "Gastroenterology",
        "text": (
            "A 50-year-old male with chronic alcoholism presents with hematemesis. "
            "Upper endoscopy reveals linear mucosal tears at the gastroesophageal junction. "
            "What is the diagnosis?"
        ),
        "options": [
            "Boerhaave Syndrome",
            "Mallory-Weiss Tear",
            "Esophageal Varices",
            "Peptic Ulcer Disease",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Gastroenterology",
        "text": "Which antibody is most sensitive and specific for screening Celiac Disease?",
        "options": [
            "Anti-Nuclear Antibody (ANA)",
            "Anti-Tissue Transglutaminase (tTG) IgA",
            "Anti-Smooth Muscle Antibody (ASMA)",
            "Anti-Neutrophil Cytoplasmic Antibody (p-ANCA)",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.MEDIUM,
    },
    {
        "topic": "Pharmacology",
        "text": "Which mechanism of action corresponds to Lisinopril?",
        "options": [
            "Beta-1 Adrenergic Receptor Antagonist",
            "Inhibition of Angiotensin-Converting Enzyme (ACE)",
            "Angiotensin II Receptor Blocker (ARB)",
            "Loop Diuretic inhibiting Na-K-2Cl cotransporter",
        ],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
    {
        "topic": "Pharmacology",
        "text": "What is the specific antidote for Acetaminophen (Paracetamol) toxicity?",
        "options": ["Naloxone", "N-Acetylcysteine (NAC)", "Flumazenil", "Atropine"],
        "correct_option_index": 1,
        "difficulty": DifficultyLevel.EASY,
    },
]


async def seed_data(session: AsyncSession) -> None:
    logger.info("Checking database state for existing seed data...")

    # 1. Seed Topics
    topic_map: dict[str, Topic] = {}
    for name in TOPICS_DATA:
        stmt = select(Topic).where(Topic.name == name)
        res = await session.execute(stmt)
        topic = res.scalar_one_or_none()
        if topic is None:
            topic = Topic(name=name)
            session.add(topic)
            await session.flush()
            logger.info("Created Topic: %s (ID: %s)", name, topic.id)
        topic_map[name] = topic

    # 2. Seed Questions
    questions_count = 0
    for q_data in QUESTIONS_DATA:
        topic_name = str(q_data["topic"])
        topic = topic_map.get(topic_name)
        if topic is None:
            continue

        q_text = str(q_data["text"])
        q_stmt = select(Question).where(Question.text == q_text)
        res_q = await session.execute(q_stmt)
        q_obj = res_q.scalar_one_or_none()

        if q_obj is None:
            options_list: list[str] = q_data["options"]  # type: ignore[assignment]
            correct_idx: int = q_data["correct_option_index"]  # type: ignore[assignment]
            diff: DifficultyLevel = q_data["difficulty"]  # type: ignore[assignment]
            q_obj = Question(
                text=q_text,
                options=options_list,
                correct_option_index=correct_idx,
                difficulty=diff,
                topics=[topic],
            )
            session.add(q_obj)
            questions_count += 1
            await session.flush()
            logger.info("Created Question: %s...", q_text[:40])

    await session.commit()
    logger.info("Master data seeding completed successfully! Seeded %d questions.", questions_count)
    logger.info("Tip: Run `uv run python -m scripts.seed_attempts` to generate attempts.")


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    session_factory = get_session_factory()
    async with session_factory() as session:
        await seed_data(session)


if __name__ == "__main__":
    asyncio.run(main())
