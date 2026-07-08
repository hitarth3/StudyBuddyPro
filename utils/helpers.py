from __future__ import annotations

"""
StudyBuddy Pro — Utility Helpers

Reusable utility functions used across the application.
"""

import json
import re
import uuid
from datetime import datetime


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable string (e.g. '2.4 MB')."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def truncate_text(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len characters with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def sanitize_filename(name: str) -> str:
    """Remove or replace characters unsafe for filenames."""
    safe = re.sub(r'[^\w\s\-.]', '', name)
    safe = re.sub(r'\s+', '_', safe.strip())
    return safe or "unnamed"


def generate_id() -> str:
    """Generate a short unique ID."""
    return uuid.uuid4().hex[:12]


def timestamp_now() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.utcnow().isoformat()


def parse_json_safe(text: str) -> dict | list | None:
    """
    Robustly extract and parse JSON from LLM output.

    Handles cases where the JSON is wrapped in markdown code fences
    or has trailing text after the JSON block.
    """
    if not text or not text.strip():
        return None

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code fences
    patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}',
        r'\[[\s\S]*\]',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1) if '```' in pattern else match.group(0)
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    return None


def format_sources(sources: list[dict]) -> str:
    """Format source citations for display."""
    if not sources:
        return ""

    lines = []
    for i, src in enumerate(sources, 1):
        doc = src.get("document", "Unknown")
        page = src.get("page", "?")
        text = truncate_text(src.get("text", ""), 150)
        lines.append(f"**[{i}]** {doc} — Page {page}\n> {text}")

    return "\n\n".join(lines)


def calculate_confidence(distances: list[float]) -> float:
    """
    Convert retrieval distances to a confidence percentage.

    Lower distance = higher confidence. Uses sigmoid-like mapping.
    """
    if not distances:
        return 0.0

    avg_distance = sum(distances) / len(distances)
    # Map distance to 0-100 confidence
    # Typical cosine distances range 0.2 (very close) to 1.5+ (far)
    confidence = max(0.0, min(100.0, (1.0 - avg_distance) * 100))
    return round(confidence, 1)


def format_duration(seconds: int) -> str:
    """Format seconds into human-readable duration."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
