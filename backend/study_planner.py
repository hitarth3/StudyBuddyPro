from __future__ import annotations

"""
StudyBuddy Pro — Study Planner

Generates structured study schedules based on exam date and available time.
"""

from datetime import datetime, date
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from backend.vector_store import vector_store
from prompts.templates import STUDY_PLAN_PROMPT
from utils.logger import get_logger

log = get_logger(__name__)


class StudyPlanner:
    """Generates personalized study schedules."""

    def __init__(self) -> None:
        self._llm: ChatGroq | None = None

    def _get_llm(self) -> ChatGroq:
        if self._llm is None:
            self._llm = ChatGroq(
                model=settings.llm_model,
                temperature=0.4,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries,
            )
        return self._llm

    def generate_plan(self, exam_date_str: str,
                      hours_per_day: float = 4.0,
                      topics: list[str] | None = None) -> dict:
        """
        Generate a study plan.

        Args:
            exam_date_str: Exam date as YYYY-MM-DD string.
            hours_per_day: Study hours available per day.
            topics: List of topics to cover. Auto-detected if None.

        Returns:
            Dict with "plan" (Markdown), or "error".
        """
        # Parse exam date
        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        except ValueError:
            return {"error": "Invalid date format. Please use YYYY-MM-DD."}

        today = date.today()
        days_remaining = (exam_date - today).days

        if days_remaining < 1:
            return {"error": "Exam date must be in the future."}

        # Get topics from uploaded documents
        if not topics:
            topics = self._detect_topics()

        if not topics:
            topics = ["General Study"]

        topics_text = "\n".join(f"- {t}" for t in topics)

        prompt = STUDY_PLAN_PROMPT.format(
            topics=topics_text,
            exam_date=exam_date_str,
            days_remaining=days_remaining,
            hours_per_day=hours_per_day,
        )

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert study planning advisor. Create practical, detailed study schedules."),
                HumanMessage(content=prompt),
            ])
            plan = response.content.strip()
        except Exception as e:
            log.error("Study plan generation failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {"error": "Rate limit reached. Please wait and try again."}
            return {"error": f"Failed to generate study plan: {error_msg[:100]}"}

        return {
            "plan": plan,
            "exam_date": exam_date_str,
            "days_remaining": days_remaining,
            "hours_per_day": hours_per_day,
            "topics": topics,
        }

    def _detect_topics(self) -> list[str]:
        """Auto-detect topics from uploaded documents."""
        docs = vector_store.get_all_documents()
        if not docs:
            return []

        # Use document names as topic seeds
        topics = []
        for doc_name in docs:
            # Strip extension and clean up
            name = doc_name.rsplit(".", 1)[0]
            name = name.replace("_", " ").replace("-", " ").title()
            topics.append(name)

        return topics


# Singleton
study_planner = StudyPlanner()
