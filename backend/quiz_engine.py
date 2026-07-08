from __future__ import annotations

"""
StudyBuddy Pro — Quiz Engine

Generates quizzes from study material and evaluates student answers using AI.
"""

import json
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from backend.vector_store import vector_store
from prompts.templates import QUIZ_GENERATION_PROMPT, QUIZ_EVALUATION_PROMPT, WEAK_TOPIC_PROMPT
from utils.logger import get_logger
from utils.helpers import parse_json_safe

log = get_logger(__name__)


class QuizEngine:
    """Generates quizzes and evaluates answers."""

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

    def generate_quiz(self, topic: str = "all topics",
                      difficulty: str = "medium",
                      num_mcq: int | None = None,
                      num_short: int | None = None) -> dict:
        """
        Generate a structured quiz from the uploaded material.

        Returns:
            Dict with "questions" list, or "error" key on failure.
        """
        num_mcq = num_mcq or settings.quiz_mcq_count
        num_short = num_short or settings.quiz_short_count

        # Get context from vector store
        context = vector_store.get_context_for_topic(topic, k=8)

        if not context:
            return {"error": "No study material found. Please upload documents first."}

        prompt = QUIZ_GENERATION_PROMPT.format(
            context=context,
            topic=topic,
            difficulty=difficulty,
            num_mcq=num_mcq,
            num_short=num_short,
        )

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert quiz generator. Return ONLY valid JSON."),
                HumanMessage(content=prompt),
            ])
            raw = response.content.strip()
        except Exception as e:
            log.error("Quiz generation failed: %s", e)
            error_msg = str(e)
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                return {"error": "Rate limit reached. Please wait a moment and try again."}
            return {"error": f"Failed to generate quiz: {error_msg[:100]}"}

        # Parse JSON
        parsed = parse_json_safe(raw)
        if parsed is None:
            log.warning("Failed to parse quiz JSON: %s", raw[:200])
            return {"error": "Failed to parse quiz response. Please try again."}

        # Validate structure
        if isinstance(parsed, dict) and "questions" in parsed:
            questions = parsed["questions"]
        elif isinstance(parsed, list):
            questions = parsed
        else:
            return {"error": "Unexpected quiz format. Please try again."}

        # Ensure IDs
        for i, q in enumerate(questions):
            q.setdefault("id", i + 1)
            q.setdefault("type", "mcq" if i < num_mcq else "short_answer")
            q.setdefault("difficulty", difficulty)
            q.setdefault("topic", topic)

        log.info("Generated quiz with %d questions on '%s'", len(questions), topic)
        return {"questions": questions, "topic": topic, "difficulty": difficulty}

    def evaluate_answers(self, questions: list[dict],
                         user_answers: dict[int, str]) -> dict:
        """
        Evaluate user answers against correct answers.

        Args:
            questions: List of question dicts from generate_quiz.
            user_answers: Dict mapping question ID to user's answer string.

        Returns:
            Dict with results, total_marks, max_marks, percentage.
        """
        if not questions or not user_answers:
            return {"error": "No questions or answers to evaluate."}

        # Build QA pairs for evaluation
        qa_pairs = []
        for q in questions:
            qid = q.get("id", 0)
            user_ans = user_answers.get(qid, "")
            qa_pairs.append({
                "question_id": qid,
                "type": q.get("type", "mcq"),
                "question": q.get("question", ""),
                "correct_answer": q.get("correct_answer", ""),
                "user_answer": user_ans,
                "options": q.get("options", []),
            })

        prompt = QUIZ_EVALUATION_PROMPT.format(
            qa_pairs=json.dumps(qa_pairs, indent=2)
        )

        try:
            llm = self._get_llm()
            response = llm.invoke([
                SystemMessage(content="You are an expert exam evaluator. Return ONLY valid JSON."),
                HumanMessage(content=prompt),
            ])
            raw = response.content.strip()
        except Exception as e:
            log.error("Answer evaluation failed: %s", e)
            # Fallback: do simple matching for MCQs
            return self._fallback_evaluate(questions, user_answers)

        parsed = parse_json_safe(raw)
        if parsed is None:
            log.warning("Failed to parse evaluation JSON, using fallback")
            return self._fallback_evaluate(questions, user_answers)

        return parsed

    def _fallback_evaluate(self, questions: list[dict],
                           user_answers: dict[int, str]) -> dict:
        """Simple rule-based evaluation fallback."""
        results = []
        total = 0.0
        max_marks = 0.0

        for q in questions:
            qid = q.get("id", 0)
            correct = q.get("correct_answer", "").strip().upper()
            user_ans = user_answers.get(qid, "").strip().upper()
            q_type = q.get("type", "mcq")

            max_marks += 1.0

            if q_type == "mcq":
                # Extract letter if user gave full option text
                user_letter = user_ans[0] if user_ans else ""
                correct_letter = correct[0] if correct else ""
                is_correct = user_letter == correct_letter
                marks = 1.0 if is_correct else 0.0
                status = "correct" if is_correct else "incorrect"
            else:
                # For short answers, do basic keyword matching
                correct_words = set(correct.lower().split())
                user_words = set(user_ans.lower().split())
                if not correct_words:
                    marks = 0.0
                    status = "incorrect"
                else:
                    overlap = len(correct_words & user_words) / len(correct_words)
                    if overlap > 0.7:
                        marks = 1.0
                        status = "correct"
                    elif overlap > 0.3:
                        marks = 0.5
                        status = "partial"
                    else:
                        marks = 0.0
                        status = "incorrect"

            total += marks
            results.append({
                "question_id": qid,
                "status": status,
                "marks": marks,
                "max_marks": 1.0,
                "explanation": q.get("explanation", ""),
            })

        return {
            "results": results,
            "total_marks": total,
            "max_marks": max_marks,
            "percentage": round((total / max_marks * 100) if max_marks > 0 else 0, 1),
            "summary": f"You scored {total}/{max_marks} ({round(total / max_marks * 100) if max_marks > 0 else 0}%)",
        }

    def analyze_weak_topics(self, quiz_history: list[dict]) -> dict:
        """Analyze quiz history to identify weak topics."""
        if not quiz_history:
            return {"weak_topics": [], "strong_topics": [],
                    "overall_recommendation": "Take some quizzes first to get topic analysis."}

        # Build topic stats from history
        topic_stats: dict[str, dict] = {}

        for quiz in quiz_history:
            for result in quiz.get("results", []):
                topic = result.get("topic", quiz.get("topic", "General"))
                if topic not in topic_stats:
                    topic_stats[topic] = {"correct": 0, "total": 0, "mistakes": []}

                topic_stats[topic]["total"] += 1
                if result.get("status") == "correct":
                    topic_stats[topic]["correct"] += 1
                elif result.get("status") == "incorrect":
                    q_text = result.get("question", "")
                    if q_text:
                        topic_stats[topic]["mistakes"].append(q_text[:100])

        # Build weak/strong lists
        weak_topics = []
        strong_topics = []

        for topic, stats in topic_stats.items():
            accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            entry = {
                "topic": topic,
                "accuracy": round(accuracy, 1),
                "times_tested": stats["total"],
            }
            if accuracy < 60:
                entry["common_mistakes"] = stats["mistakes"][:3]
                entry["recommendation"] = f"Review '{topic}' concepts and practice more questions."
                weak_topics.append(entry)
            else:
                strong_topics.append(entry)

        weak_topics.sort(key=lambda x: x["accuracy"])
        strong_topics.sort(key=lambda x: x["accuracy"], reverse=True)

        overall = "Great job! Keep practicing." if not weak_topics else \
            f"Focus on these weak areas: {', '.join(t['topic'] for t in weak_topics[:3])}"

        return {
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "overall_recommendation": overall,
        }


# Singleton
quiz_engine = QuizEngine()
