from __future__ import annotations

"""
StudyBuddy Pro — Session Persistence

JSON-file based persistence layer for storing session data:
chat history, quiz history, weak topics, study plans, and settings.
"""

import json
import threading
from pathlib import Path
from typing import Any

from config.settings import settings
from utils.logger import get_logger
from utils.helpers import timestamp_now

log = get_logger(__name__)

_lock = threading.Lock()
_SESSION_FILE = "session.json"


def _session_path() -> Path:
    """Get the path to the session file."""
    settings.ensure_directories()
    return settings.sessions_dir / _SESSION_FILE


def _load_raw() -> dict[str, Any]:
    """Load the raw session dict from disk."""
    path = _session_path()
    if not path.exists():
        return _default_session()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, OSError) as e:
        log.warning("Failed to load session file, resetting: %s", e)
        return _default_session()


def _save_raw(data: dict[str, Any]) -> None:
    """Write session dict to disk."""
    path = _session_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except OSError as e:
        log.error("Failed to save session: %s", e)


def _default_session() -> dict[str, Any]:
    """Return a blank session structure."""
    return {
        "uploaded_files": [],
        "chat_history": [],
        "quiz_history": [],
        "weak_topics": [],
        "study_plans": [],
        "flashcard_sets": [],
        "settings": {
            "theme": "dark",
            "explain_mode": "default",
            "difficulty": "medium",
        },
        "analytics": {
            "total_quizzes": 0,
            "total_questions_answered": 0,
            "total_correct": 0,
            "total_study_time_seconds": 0,
            "daily_activity": {},
        },
        "last_updated": timestamp_now(),
    }


class SessionMemory:
    """Thread-safe session memory manager."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load session from disk."""
        with _lock:
            self._data = _load_raw()
        log.info("Session loaded (%d files, %d quizzes)",
                 len(self._data.get("uploaded_files", [])),
                 len(self._data.get("quiz_history", [])))

    def save(self) -> None:
        """Persist session to disk."""
        with _lock:
            self._data["last_updated"] = timestamp_now()
            _save_raw(self._data)

    def reset(self) -> None:
        """Reset session to defaults."""
        with _lock:
            self._data = _default_session()
            _save_raw(self._data)
        log.info("Session reset")

    # --- Uploaded Files ---

    def get_uploaded_files(self) -> list[dict]:
        return self._data.get("uploaded_files", [])

    def add_uploaded_file(self, file_info: dict) -> None:
        """Add a file record: {name, path, pages, chunks, size, uploaded_at}."""
        self._data.setdefault("uploaded_files", []).append(file_info)
        self.save()

    def remove_uploaded_file(self, filename: str) -> None:
        self._data["uploaded_files"] = [
            f for f in self._data.get("uploaded_files", [])
            if f.get("name") != filename
        ]
        self.save()

    # --- Chat History ---

    def get_chat_history(self) -> list[dict]:
        return self._data.get("chat_history", [])

    def add_chat_message(self, role: str, content: str,
                         sources: list[dict] | None = None) -> None:
        msg = {"role": role, "content": content, "timestamp": timestamp_now()}
        if sources:
            msg["sources"] = sources
        self._data.setdefault("chat_history", []).append(msg)
        # Keep last N messages
        max_hist = settings.max_chat_history * 2  # user + assistant pairs
        self._data["chat_history"] = self._data["chat_history"][-max_hist:]
        self.save()

    def clear_chat_history(self) -> None:
        self._data["chat_history"] = []
        self.save()

    # --- Quiz History ---

    def get_quiz_history(self) -> list[dict]:
        return self._data.get("quiz_history", [])

    def add_quiz_result(self, result: dict) -> None:
        """Add quiz result: {timestamp, topic, score, max_score, results, ...}."""
        result["timestamp"] = timestamp_now()
        self._data.setdefault("quiz_history", []).append(result)
        # Update analytics
        analytics = self._data.setdefault("analytics", {})
        analytics["total_quizzes"] = analytics.get("total_quizzes", 0) + 1
        q_count = len(result.get("results", []))
        correct = sum(1 for r in result.get("results", []) if r.get("status") == "correct")
        analytics["total_questions_answered"] = analytics.get("total_questions_answered", 0) + q_count
        analytics["total_correct"] = analytics.get("total_correct", 0) + correct

        from datetime import date
        today = date.today().isoformat()
        daily = analytics.setdefault("daily_activity", {})
        daily[today] = daily.get(today, 0) + 1

        self.save()

    # --- Weak Topics ---

    def get_weak_topics(self) -> list[dict]:
        return self._data.get("weak_topics", [])

    def set_weak_topics(self, topics: list[dict]) -> None:
        self._data["weak_topics"] = topics
        self.save()

    # --- Study Plans ---

    def get_study_plans(self) -> list[dict]:
        return self._data.get("study_plans", [])

    def add_study_plan(self, plan: dict) -> None:
        plan["created_at"] = timestamp_now()
        self._data.setdefault("study_plans", []).append(plan)
        self.save()

    # --- Flashcards ---

    def get_flashcard_sets(self) -> list[dict]:
        return self._data.get("flashcard_sets", [])

    def add_flashcard_set(self, cards: dict) -> None:
        cards["created_at"] = timestamp_now()
        self._data.setdefault("flashcard_sets", []).append(cards)
        self.save()

    # --- Settings ---

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._data.get("settings", {}).get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self._data.setdefault("settings", {})[key] = value
        self.save()

    # --- Analytics ---

    def get_analytics(self) -> dict:
        return self._data.get("analytics", {})

    def add_study_time(self, seconds: int) -> None:
        analytics = self._data.setdefault("analytics", {})
        analytics["total_study_time_seconds"] = \
            analytics.get("total_study_time_seconds", 0) + seconds
        self.save()


# Singleton instance
session_memory = SessionMemory()
