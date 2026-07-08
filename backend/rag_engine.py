from __future__ import annotations

"""
StudyBuddy Pro — RAG Engine

Full Retrieval-Augmented Generation pipeline:
Query → Rewrite → Retrieve (MMR, top-5) → LLM → Answer with citations.
"""

import re
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from backend.vector_store import vector_store
from prompts.templates import (
    RAG_SYSTEM_PROMPT, RAG_USER_PROMPT, QUERY_REWRITE_PROMPT,
    EXPLAIN_MODES, DIFFICULTY_MODES,
)
from utils.logger import get_logger

log = get_logger(__name__)


class RAGEngine:
    """Handles the complete RAG pipeline for answering questions."""

    def __init__(self) -> None:
        self._llm: ChatGroq | None = None

    def _get_llm(self) -> ChatGroq:
        """Lazy-load the LLM."""
        if self._llm is None:
            self._llm = ChatGroq(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries,
            )
            log.info("LLM initialized: %s", settings.llm_model)
        return self._llm

    def _rewrite_query(self, question: str, chat_history: list[dict]) -> str:
        """Rewrite the question using conversation context for better retrieval."""
        if not chat_history:
            return question

        history_text = self._format_chat_history(chat_history[-6:])  # Last 3 turns

        try:
            llm = self._get_llm()
            prompt = QUERY_REWRITE_PROMPT.format(
                chat_history=history_text,
                question=question,
            )
            response = llm.invoke([HumanMessage(content=prompt)])
            rewritten = response.content.strip()
            if rewritten:
                log.debug("Query rewritten: '%s' → '%s'", question, rewritten)
                return rewritten
        except Exception as e:
            log.warning("Query rewrite failed, using original: %s", e)

        return question

    def _format_chat_history(self, history: list[dict]) -> str:
        """Format chat history for prompt inclusion."""
        if not history:
            return "No previous conversation."

        lines = []
        for msg in history:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            if len(content) > 300:
                content = content[:300] + "..."
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def _extract_confidence(self, answer: str) -> tuple[str, float]:
        """Extract confidence score from the answer text."""
        # Look for patterns like "Confidence: 85%" or "confidence assessment: 70%"
        patterns = [
            r'[Cc]onfidence[:\s]+(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*%\s*confidence',
            r'[Cc]onfidence[:\s]+(\d+(?:\.\d+)?)\s*/\s*100',
        ]

        confidence = 75.0  # Default
        clean_answer = answer

        for pattern in patterns:
            match = re.search(pattern, answer)
            if match:
                confidence = float(match.group(1))
                # Remove the confidence line from the answer
                last_para = answer.rfind("\n\n")
                if last_para > len(answer) * 0.7:
                    candidate = answer[last_para:].strip()
                    if "onfidence" in candidate.lower():
                        clean_answer = answer[:last_para].strip()
                break

        return clean_answer, min(100.0, max(0.0, confidence))

    def ask(self, question: str, chat_history: list[dict] | None = None,
            explain_mode: str = "default",
            difficulty: str = "medium") -> dict:
        """
        Answer a question using the RAG pipeline.

        Args:
            question: The user's question.
            chat_history: Previous conversation messages.
            explain_mode: One of "default", "eli10", "high_school", "college", "exam_revision".
            difficulty: One of "easy", "medium", "hard", "adaptive".

        Returns:
            Dict with keys: answer, sources, confidence, raw_answer.
        """
        chat_history = chat_history or []

        # Step 1: Rewrite query for better retrieval
        search_query = self._rewrite_query(question, chat_history)

        # Step 2: Retrieve relevant documents (MMR, top-5)
        results = vector_store.search_with_scores(search_query, k=settings.retrieval_k)

        if not results:
            return {
                "answer": "📭 **No documents found.** Please upload your study material first using the Upload tab, then come back to ask questions.",
                "sources": [],
                "confidence": 0.0,
            }

        # Step 3: Build context and sources
        context_parts = []
        sources = []
        distances = []

        for i, (doc, score) in enumerate(results):
            context_parts.append(f"[Source {i + 1}]: {doc.page_content}")
            sources.append({
                "index": i + 1,
                "document": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "?"),
                "text": doc.page_content,
                "chunk_id": doc.metadata.get("chunk_id", ""),
                "score": round(score, 3),
            })
            distances.append(1.0 - score if score <= 1.0 else score)

        context = "\n\n".join(context_parts)
        sources_text = "\n".join(
            f"Source {s['index']}: {s['document']} (Page {s['page']})"
            for s in sources
        )

        # Step 4: Build prompt
        explain_text = EXPLAIN_MODES.get(explain_mode, EXPLAIN_MODES["default"])
        difficulty_text = DIFFICULTY_MODES.get(difficulty, DIFFICULTY_MODES["medium"])

        system_prompt = RAG_SYSTEM_PROMPT.format(
            explain_mode=explain_text,
            difficulty=difficulty_text,
        )

        user_prompt = RAG_USER_PROMPT.format(
            context=context,
            sources=sources_text,
            chat_history=self._format_chat_history(chat_history[-6:]),
            question=question,
        )

        # Step 5: Call LLM
        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            raw_answer = response.content.strip()
        except Exception as e:
            log.error("LLM call failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {
                    "answer": "⏳ **Rate limit reached.** The AI service is temporarily busy. Please wait a moment and try again.",
                    "sources": sources,
                    "confidence": 0.0,
                }
            return {
                "answer": f"❌ **Error generating response.** Please try again. ({error_msg[:100]})",
                "sources": sources,
                "confidence": 0.0,
            }

        # Step 6: Extract confidence
        answer, confidence = self._extract_confidence(raw_answer)

        # Step 7: Check confidence threshold
        if confidence < settings.confidence_threshold * 100:
            answer += (
                "\n\n---\n⚠️ **Low Confidence Warning**: The uploaded notes may not contain "
                "sufficient information to fully answer this question. Consider uploading "
                "more material on this topic."
            )

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
        }


# Singleton
rag_engine = RAGEngine()
