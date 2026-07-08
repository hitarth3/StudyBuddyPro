from __future__ import annotations

"""
StudyBuddy Pro — Analytics Engine

Generates analytics data for charts and performance tracking.
"""

from datetime import date, timedelta

from memory.persistence import session_memory
from utils.logger import get_logger

log = get_logger(__name__)


class AnalyticsEngine:
    """Processes quiz and study data into chart-ready formats."""

    def get_quiz_scores(self) -> dict:
        """Get quiz scores over time for line chart."""
        history = session_memory.get_quiz_history()
        if not history:
            return {"labels": [], "scores": [], "has_data": False}

        labels = []
        scores = []
        for i, quiz in enumerate(history):
            label = f"Quiz {i + 1}"
            timestamp = quiz.get("timestamp", "")
            if timestamp:
                try:
                    label = timestamp[:10]
                except (IndexError, TypeError):
                    pass
            labels.append(label)
            scores.append(quiz.get("percentage", 0))

        return {"labels": labels, "scores": scores, "has_data": True}

    def get_topic_accuracy(self) -> dict:
        """Get per-topic accuracy for bar chart."""
        history = session_memory.get_quiz_history()
        if not history:
            return {"topics": [], "accuracy": [], "has_data": False}

        topic_stats: dict[str, dict] = {}

        for quiz in history:
            for result in quiz.get("results", []):
                topic = result.get("topic", quiz.get("topic", "General"))
                if topic not in topic_stats:
                    topic_stats[topic] = {"correct": 0, "total": 0}
                topic_stats[topic]["total"] += 1
                if result.get("status") == "correct":
                    topic_stats[topic]["correct"] += 1

        topics = []
        accuracy = []
        for topic, stats in sorted(topic_stats.items()):
            topics.append(topic)
            acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            accuracy.append(round(acc, 1))

        return {"topics": topics, "accuracy": accuracy, "has_data": True}

    def get_weak_strong_topics(self) -> dict:
        """Get weak vs strong topics."""
        data = self.get_topic_accuracy()
        if not data["has_data"]:
            return {"weak": [], "strong": [], "has_data": False}

        weak = []
        strong = []
        for topic, acc in zip(data["topics"], data["accuracy"]):
            entry = {"topic": topic, "accuracy": acc}
            if acc < 60:
                weak.append(entry)
            else:
                strong.append(entry)

        weak.sort(key=lambda x: x["accuracy"])
        strong.sort(key=lambda x: x["accuracy"], reverse=True)

        return {"weak": weak, "strong": strong, "has_data": True}

    def get_overall_stats(self) -> dict:
        """Get overall performance statistics."""
        analytics = session_memory.get_analytics()
        history = session_memory.get_quiz_history()
        files = session_memory.get_uploaded_files()

        total_quizzes = analytics.get("total_quizzes", 0)
        total_questions = analytics.get("total_questions_answered", 0)
        total_correct = analytics.get("total_correct", 0)
        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0

        # Calculate study streak
        daily = analytics.get("daily_activity", {})
        streak = self._calculate_streak(daily)

        # Average score
        avg_score = 0
        if history:
            scores = [q.get("percentage", 0) for q in history]
            avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_documents": len(files),
            "total_quizzes": total_quizzes,
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": round(overall_accuracy, 1),
            "average_score": round(avg_score, 1),
            "study_streak": streak,
            "study_time_seconds": analytics.get("total_study_time_seconds", 0),
        }

    def _calculate_streak(self, daily_activity: dict) -> int:
        """Calculate consecutive study days ending today."""
        if not daily_activity:
            return 0

        today = date.today()
        streak = 0
        current = today

        while True:
            date_str = current.isoformat()
            if date_str in daily_activity:
                streak += 1
                current -= timedelta(days=1)
            else:
                break

        return streak

    def get_activity_data(self) -> dict:
        """Get daily activity data for heatmap."""
        analytics = session_memory.get_analytics()
        daily = analytics.get("daily_activity", {})

        if not daily:
            return {"dates": [], "counts": [], "has_data": False}

        dates = sorted(daily.keys())
        counts = [daily[d] for d in dates]

        return {"dates": dates, "counts": counts, "has_data": True}


# Singleton
analytics_engine = AnalyticsEngine()
