from __future__ import annotations

"""
StudyBuddy Pro — Export Engine

Exports quizzes, flashcards, study plans, and revision notes to Markdown files.
"""

from pathlib import Path
from datetime import datetime

from config.settings import settings
from utils.logger import get_logger
from utils.helpers import sanitize_filename

log = get_logger(__name__)


class ExportEngine:
    """Exports study materials to downloadable files."""

    def __init__(self) -> None:
        settings.ensure_directories()

    def _get_export_path(self, name: str) -> Path:
        """Generate a unique export file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sanitize_filename(name)}_{timestamp}.md"
        return settings.exports_dir / filename

    def export_quiz(self, quiz_data: dict) -> str | None:
        """
        Export quiz to a Markdown file.

        Returns:
            File path string, or None on failure.
        """
        if not quiz_data or "questions" not in quiz_data:
            return None

        lines = [
            f"# 📝 Quiz — {quiz_data.get('topic', 'General')}",
            f"**Difficulty:** {quiz_data.get('difficulty', 'Medium')}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
        ]

        for q in quiz_data["questions"]:
            qid = q.get("id", 0)
            q_type = q.get("type", "mcq")
            question = q.get("question", "")

            lines.append(f"## Question {qid}")
            lines.append(f"**Type:** {q_type.upper()} | **Difficulty:** {q.get('difficulty', '?')} | **Topic:** {q.get('topic', '?')}")
            lines.append("")
            lines.append(question)
            lines.append("")

            if q_type == "mcq" and q.get("options"):
                for opt in q["options"]:
                    lines.append(f"- {opt}")
                lines.append("")

            lines.append(f"**✅ Correct Answer:** {q.get('correct_answer', 'N/A')}")
            lines.append("")
            lines.append(f"**💡 Explanation:** {q.get('explanation', 'N/A')}")
            lines.append("")
            lines.append("---")
            lines.append("")

        path = self._get_export_path("quiz")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            log.info("Exported quiz to %s", path)
            return str(path)
        except OSError as e:
            log.error("Failed to export quiz: %s", e)
            return None

    def export_flashcards(self, flashcard_data: dict) -> str | None:
        """Export flashcards to a Markdown file."""
        cards = flashcard_data.get("flashcards", [])
        if not cards:
            return None

        lines = [
            f"# 🃏 Flashcards — {flashcard_data.get('topic', 'General')}",
            f"**Count:** {len(cards)}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
        ]

        for card in cards:
            lines.append(f"### Card {card.get('id', '?')}")
            lines.append(f"**Q:** {card.get('front', '')}")
            lines.append("")
            lines.append(f"**A:** {card.get('back', '')}")
            lines.append("")
            lines.append("---")
            lines.append("")

        path = self._get_export_path("flashcards")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            log.info("Exported flashcards to %s", path)
            return str(path)
        except OSError as e:
            log.error("Failed to export flashcards: %s", e)
            return None

    def export_study_plan(self, plan_data: dict) -> str | None:
        """Export study plan to a Markdown file."""
        plan = plan_data.get("plan", "")
        if not plan:
            return None

        lines = [
            "# 📅 Study Plan",
            f"**Exam Date:** {plan_data.get('exam_date', 'N/A')}",
            f"**Days Remaining:** {plan_data.get('days_remaining', '?')}",
            f"**Hours/Day:** {plan_data.get('hours_per_day', '?')}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            plan,
        ]

        path = self._get_export_path("study_plan")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            log.info("Exported study plan to %s", path)
            return str(path)
        except OSError as e:
            log.error("Failed to export study plan: %s", e)
            return None

    def export_revision_notes(self, notes_data: dict) -> str | None:
        """Export revision notes to a Markdown file."""
        notes = notes_data.get("notes", "")
        if not notes:
            return None

        lines = [
            f"# 📚 Revision Notes — {notes_data.get('topic', 'General')}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            notes,
        ]

        path = self._get_export_path("revision_notes")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            log.info("Exported revision notes to %s", path)
            return str(path)
        except OSError as e:
            log.error("Failed to export revision notes: %s", e)
            return None

    def export_summary(self, summary_data: dict) -> str | None:
        """Export summary to a Markdown file."""
        summary = summary_data.get("summary", "")
        if not summary:
            return None

        lines = [
            f"# {summary_data.get('mode_label', '📝 Summary')}",
            f"**Topic:** {summary_data.get('topic', 'All Topics')}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
            summary,
        ]

        path = self._get_export_path("summary")
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
            log.info("Exported summary to %s", path)
            return str(path)
        except OSError as e:
            log.error("Failed to export summary: %s", e)
            return None


# Singleton
export_engine = ExportEngine()
