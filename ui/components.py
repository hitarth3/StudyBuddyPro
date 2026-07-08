from __future__ import annotations

"""
StudyBuddy Pro — Reusable UI Components

Helper functions for building consistent UI elements.
"""


def icon(name: str) -> str:
    """Return an emoji icon by name."""
    icons = {
        "dashboard": "🏠",
        "upload": "📤",
        "chat": "💬",
        "quiz": "📝",
        "flashcards": "🃏",
        "revision": "📚",
        "planner": "📅",
        "summary": "📄",
        "search": "🔍",
        "analytics": "📊",
        "export": "💾",
        "settings": "⚙️",
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "star": "⭐",
        "fire": "🔥",
        "trophy": "🏆",
        "brain": "🧠",
        "target": "🎯",
        "book": "📖",
        "clock": "⏰",
        "check": "✓",
        "arrow_right": "→",
        "sparkle": "✨",
        "rocket": "🚀",
        "light": "💡",
        "pin": "📌",
        "chart": "📈",
        "doc": "📄",
        "pdf": "📕",
        "file": "📁",
        "delete": "🗑️",
        "download": "⬇️",
        "refresh": "🔄",
        "play": "▶️",
        "pause": "⏸️",
        "next": "⏭️",
        "prev": "⏮️",
        "shuffle": "🔀",
        "flip": "🔃",
    }
    return icons.get(name, "•")


def stat_card_html(title: str, value: str, subtitle: str = "",
                   icon_name: str = "") -> str:
    """Generate HTML for a statistic card."""
    ic = icon(icon_name) if icon_name else ""
    sub = f'<p style="color: var(--sb-text-secondary); font-size: 13px; margin: 4px 0 0 0;">{subtitle}</p>' if subtitle else ""
    return f"""
    <div style="background: var(--sb-bg-card); border: 1px solid var(--sb-border); border-radius: 16px;
                padding: 24px; transition: all 0.3s ease; box-shadow: var(--sb-shadow);">
        <div style="font-size: 14px; color: var(--sb-text-secondary); font-weight: 500; margin-bottom: 8px;">
            {ic} {title}
        </div>
        <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;">
            {value}
        </div>
        {sub}
    </div>
    """


def empty_state_html(title: str, description: str, icon_name: str = "info") -> str:
    """Generate HTML for an empty state."""
    ic = icon(icon_name)
    return f"""
    <div class="empty-state">
        <div class="icon">{ic}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """


def confidence_badge_html(confidence: float) -> str:
    """Generate a confidence score badge."""
    if confidence >= 80:
        cls = "badge-success"
        label = "High Confidence"
    elif confidence >= 60:
        cls = "badge-warning"
        label = "Medium Confidence"
    else:
        cls = "badge-error"
        label = "Low Confidence"

    return f'<span class="badge {cls}">🎯 {confidence:.0f}% — {label}</span>'


def file_info_html(files: list[dict]) -> str:
    """Generate HTML for the uploaded files list."""
    if not files:
        return empty_state_html(
            "No Documents Uploaded",
            "Upload PDF, DOCX, or TXT files to get started with your AI study assistant.",
            "upload"
        )

    rows = []
    for f in files:
        ext = f.get("extension", "").replace(".", "").upper()
        ext_badge = {
            "PDF": "📕",
            "DOCX": "📘",
            "TXT": "📄"
        }.get(ext, "📄")

        rows.append(f"""
        <div class="file-item">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 24px;">{ext_badge}</span>
                <div>
                    <div style="font-weight: 600; color: var(--sb-text-primary); font-size: 14px;">{f.get('name', 'Unknown')}</div>
                    <div style="color: var(--sb-text-secondary); font-size: 12px; margin-top: 2px;">
                        {f.get('pages', '?')} pages • {f.get('chunks', '?')} chunks • {f.get('size', '?')}
                    </div>
                </div>
            </div>
        </div>
        """)

    return "\n".join(rows)


def source_citation_html(sources: list[dict]) -> str:
    """Generate HTML for source citations."""
    if not sources:
        return ""

    parts = []
    for src in sources:
        idx = src.get("index", "?")
        doc = src.get("document", "Unknown")
        page = src.get("page", "?")
        text = src.get("text", "")
        if len(text) > 200:
            text = text[:200] + "..."
        score = src.get("score", 0)

        parts.append(f"""
        <div class="source-citation">
            <strong>[Source {idx}]</strong> {doc} — Page {page}
            <span class="badge badge-info" style="margin-left: 8px;">Score: {score}</span>
            <p style="margin: 8px 0 0 0; color: var(--sb-text-secondary); font-size: 13px;">{text}</p>
        </div>
        """)

    return "\n".join(parts)


def quiz_result_html(results: dict) -> str:
    """Generate HTML for quiz results."""
    if not results or "results" not in results:
        return ""

    total = results.get("total_marks", 0)
    max_marks = results.get("max_marks", 0)
    percentage = results.get("percentage", 0)

    # Score display
    if percentage >= 80:
        grade_emoji = "🏆"
        grade_text = "Excellent!"
    elif percentage >= 60:
        grade_emoji = "👍"
        grade_text = "Good Job!"
    elif percentage >= 40:
        grade_emoji = "📝"
        grade_text = "Keep Practicing"
    else:
        grade_emoji = "💪"
        grade_text = "More Study Needed"

    html = f"""
    <div style="text-align: center; padding: 24px;">
        <div style="font-size: 48px; margin-bottom: 8px;">{grade_emoji}</div>
        <div class="score-display">{percentage:.0f}%</div>
        <div style="font-size: 18px; font-weight: 600; color: var(--sb-text-secondary); margin-bottom: 4px;">
            {grade_text}
        </div>
        <div style="font-size: 14px; color: var(--sb-text-muted);">
            {total}/{max_marks} marks
        </div>
    </div>
    <hr style="border-color: var(--sb-border); margin: 24px 0;">
    """

    # Per-question results
    for r in results.get("results", []):
        status = r.get("status", "incorrect")
        status_class = {
            "correct": "result-correct",
            "incorrect": "result-incorrect",
            "partial": "result-partial",
        }.get(status, "")

        status_icon = {"correct": "✅", "incorrect": "❌", "partial": "⚠️"}.get(status, "•")
        marks = r.get("marks", 0)
        max_m = r.get("max_marks", 1)

        html += f"""
        <div class="quiz-question {status_class}" style="margin: 8px 0; padding: 16px; border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 600; color: var(--sb-text-primary);">Question {r.get('question_id', '?')}</span>
                <span>{status_icon} {marks}/{max_m}</span>
            </div>
            <p style="color: var(--sb-text-secondary); font-size: 13px; line-height: 1.6; margin: 0;">
                {r.get('explanation', '')}
            </p>
        </div>
        """

    return html
