from __future__ import annotations

"""
StudyBuddy Pro — Flashcard Engine

Generates flashcard sets from study material using AI.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from backend.vector_store import vector_store
from prompts.templates import FLASHCARD_GENERATION_PROMPT
from utils.logger import get_logger
from utils.helpers import parse_json_safe

log = get_logger(__name__)


class FlashcardEngine:
    """Generates and manages flashcard sets."""

    def __init__(self) -> None:
        self._llm: ChatGroq | None = None

    def _get_llm(self) -> ChatGroq:
        if self._llm is None:
            self._llm = ChatGroq(
                model=settings.llm_model,
                temperature=0.5,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries,
            )
        return self._llm

    def generate_flashcards(self, topic: str = "all topics",
                            count: int | None = None) -> dict:
        """
        Generate flashcards from uploaded material.

        Returns:
            Dict with "flashcards" list, or "error" key on failure.
        """
        count = count or settings.flashcard_default_count

        context = vector_store.get_context_for_topic(topic, k=6)
        if not context:
            return {"error": "No study material found. Please upload documents first."}

        prompt = FLASHCARD_GENERATION_PROMPT.format(
            context=context,
            topic=topic,
            count=count,
        )

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert flashcard creator. Return ONLY valid JSON."),
                HumanMessage(content=prompt),
            ])
            raw = response.content.strip()
        except Exception as e:
            log.error("Flashcard generation failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {"error": "Rate limit reached. Please wait and try again."}
            return {"error": f"Failed to generate flashcards: {error_msg[:100]}"}

        parsed = parse_json_safe(raw)
        if parsed is None:
            return {"error": "Failed to parse flashcard response. Please try again."}

        if isinstance(parsed, dict) and "flashcards" in parsed:
            cards = parsed["flashcards"]
        elif isinstance(parsed, list):
            cards = parsed
        else:
            return {"error": "Unexpected flashcard format. Please try again."}

        # Ensure IDs
        for i, card in enumerate(cards):
            card.setdefault("id", i + 1)
            card.setdefault("topic", topic)
            card.setdefault("difficulty", "medium")

        log.info("Generated %d flashcards for topic '%s'", len(cards), topic)
        return {"flashcards": cards, "topic": topic}


# Singleton
flashcard_engine = FlashcardEngine()
