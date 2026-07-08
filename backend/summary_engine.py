from __future__ import annotations

"""
StudyBuddy Pro — Summary Engine

Generates various types of summaries from study material using AI.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from backend.vector_store import vector_store
from prompts.templates import (
    SUMMARY_SHORT_PROMPT, SUMMARY_DETAILED_PROMPT, SUMMARY_BULLETS_PROMPT,
    SUMMARY_ONE_PAGE_PROMPT, SUMMARY_MIND_MAP_PROMPT, REVISION_NOTES_PROMPT,
)
from utils.logger import get_logger

log = get_logger(__name__)

_SUMMARY_PROMPTS = {
    "short": SUMMARY_SHORT_PROMPT,
    "detailed": SUMMARY_DETAILED_PROMPT,
    "bullets": SUMMARY_BULLETS_PROMPT,
    "one_page": SUMMARY_ONE_PAGE_PROMPT,
    "mind_map": SUMMARY_MIND_MAP_PROMPT,
}

_SUMMARY_LABELS = {
    "short": "📝 Short Summary",
    "detailed": "📖 Detailed Summary",
    "bullets": "📋 Bullet Point Notes",
    "one_page": "📄 One-Page Study Sheet",
    "mind_map": "🗺️ Mind Map",
}


class SummaryEngine:
    """Generates summaries and revision notes."""

    def __init__(self) -> None:
        self._llm: ChatGroq | None = None

    def _get_llm(self) -> ChatGroq:
        if self._llm is None:
            self._llm = ChatGroq(
                model=settings.llm_model,
                temperature=0.3,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries,
            )
        return self._llm

    def generate_summary(self, mode: str = "short",
                         topic: str = "all topics") -> dict:
        """
        Generate a summary of the uploaded material.

        Args:
            mode: One of "short", "detailed", "bullets", "one_page", "mind_map".
            topic: Topic to focus on.

        Returns:
            Dict with "summary" and "mode_label", or "error".
        """
        if mode not in _SUMMARY_PROMPTS:
            return {"error": f"Unknown summary mode: {mode}"}

        context = vector_store.get_context_for_topic(topic, k=8)
        if not context:
            return {"error": "No study material found. Please upload documents first."}

        prompt_template = _SUMMARY_PROMPTS[mode]
        prompt = prompt_template.format(context=context)

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert study material summarizer. Create clear, well-structured summaries."),
                HumanMessage(content=prompt),
            ])
            summary = response.content.strip()
        except Exception as e:
            log.error("Summary generation failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {"error": "Rate limit reached. Please wait and try again."}
            return {"error": f"Failed to generate summary: {error_msg[:100]}"}

        return {
            "summary": summary,
            "mode": mode,
            "mode_label": _SUMMARY_LABELS.get(mode, mode),
            "topic": topic,
        }

    def generate_revision_notes(self, topic: str = "all topics") -> dict:
        """Generate comprehensive revision notes."""
        context = vector_store.get_context_for_topic(topic, k=8)
        if not context:
            return {"error": "No study material found. Please upload documents first."}

        prompt = REVISION_NOTES_PROMPT.format(context=context, topic=topic)

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert tutor creating revision notes for exam preparation. Be thorough and practical."),
                HumanMessage(content=prompt),
            ])
            notes = response.content.strip()
        except Exception as e:
            log.error("Revision notes generation failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {"error": "Rate limit reached. Please wait and try again."}
            return {"error": f"Failed to generate revision notes: {error_msg[:100]}"}

        return {
            "notes": notes,
            "topic": topic,
        }


# Singleton
summary_engine = SummaryEngine()
