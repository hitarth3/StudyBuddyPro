from __future__ import annotations

"""
StudyBuddy Pro — Flashcards Tab

Interactive flashcards with flip animation, navigation, and shuffle.
"""

import random
import gradio as gr

from backend.flashcard_engine import flashcard_engine
from memory.persistence import session_memory
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_flashcards_tab() -> None:
    """Build the flashcards tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>🃏 Flashcards</h3>
    </div>
    """)

    # Generation controls
    with gr.Row():
        fc_topic = gr.Textbox(
            label="Topic",
            placeholder="e.g., Key Definitions, Chapter 2",
            value="all topics",
            elem_classes=["input-field"],
            scale=2,
        )
        fc_count = gr.Slider(minimum=5, maximum=20, value=10, step=1,
                             label="Number of Cards", scale=1)
        fc_generate_btn = gr.Button("✨ Generate Flashcards",
                                    elem_classes=["primary-btn"], scale=1)

    # Status
    fc_status = gr.HTML(value="", elem_id="fc-status")

    # Flashcard display
    flashcard_display = gr.HTML(
        value=empty_state_html(
            "No Flashcards Yet",
            "Generate flashcards from your study material to start reviewing.",
            "flashcards"
        ),
        elem_id="flashcard-display",
    )

    # Navigation controls
    with gr.Row():
        prev_btn = gr.Button("⏮️ Previous", elem_classes=["secondary-btn"])
        flip_btn = gr.Button("🔃 Flip Card", elem_classes=["primary-btn"])
        next_btn = gr.Button("⏭️ Next", elem_classes=["secondary-btn"])
    with gr.Row():
        shuffle_btn = gr.Button("🔀 Shuffle", elem_classes=["secondary-btn"], size="sm")

    # Progress
    progress_display = gr.HTML(value="", elem_id="fc-progress")

    # --- State ---
    cards_state = gr.State([])      # List of flashcard dicts
    index_state = gr.State(0)       # Current card index
    flipped_state = gr.State(False) # Whether card is flipped

    # --- Callbacks ---
    def _generate(topic: str, count: int):
        """Generate new flashcards."""
        result = flashcard_engine.generate_flashcards(topic=topic, count=int(count))

        if "error" in result:
            return (
                f'<span class="badge badge-error">❌ {result["error"]}</span>',
                empty_state_html("Generation Failed", result["error"], "error"),
                [],
                0,
                False,
                "",
            )

        cards = result.get("flashcards", [])
        if not cards:
            return (
                '<span class="badge badge-warning">⚠️ No flashcards generated</span>',
                empty_state_html("No Cards", "Try a different topic.", "info"),
                [],
                0,
                False,
                "",
            )

        # Save to memory
        session_memory.add_flashcard_set(result)

        return (
            f'<span class="badge badge-success">✅ {len(cards)} flashcards generated</span>',
            _render_card(cards, 0, False),
            cards,
            0,
            False,
            _render_progress(0, len(cards)),
        )

    def _flip(cards: list, idx: int, flipped: bool):
        """Flip the current card."""
        if not cards:
            return empty_state_html("No Cards", "Generate flashcards first.", "flashcards"), not flipped
        return _render_card(cards, idx, not flipped), not flipped

    def _next(cards: list, idx: int):
        """Go to next card."""
        if not cards:
            return empty_state_html("No Cards", "Generate flashcards first.", "flashcards"), idx, False, ""
        new_idx = min(idx + 1, len(cards) - 1)
        return _render_card(cards, new_idx, False), new_idx, False, _render_progress(new_idx, len(cards))

    def _prev(cards: list, idx: int):
        """Go to previous card."""
        if not cards:
            return empty_state_html("No Cards", "Generate flashcards first.", "flashcards"), idx, False, ""
        new_idx = max(idx - 1, 0)
        return _render_card(cards, new_idx, False), new_idx, False, _render_progress(new_idx, len(cards))

    def _shuffle(cards: list):
        """Shuffle cards."""
        if not cards:
            return empty_state_html("No Cards", "Generate flashcards first.", "flashcards"), cards, 0, False, ""
        shuffled = cards.copy()
        random.shuffle(shuffled)
        return (
            _render_card(shuffled, 0, False),
            shuffled,
            0,
            False,
            _render_progress(0, len(shuffled)),
        )

    # Wire events
    fc_generate_btn.click(
        fn=_generate,
        inputs=[fc_topic, fc_count],
        outputs=[fc_status, flashcard_display, cards_state, index_state,
                 flipped_state, progress_display],
    )

    flip_btn.click(
        fn=_flip,
        inputs=[cards_state, index_state, flipped_state],
        outputs=[flashcard_display, flipped_state],
    )

    next_btn.click(
        fn=_next,
        inputs=[cards_state, index_state],
        outputs=[flashcard_display, index_state, flipped_state, progress_display],
    )

    prev_btn.click(
        fn=_prev,
        inputs=[cards_state, index_state],
        outputs=[flashcard_display, index_state, flipped_state, progress_display],
    )

    shuffle_btn.click(
        fn=_shuffle,
        inputs=[cards_state],
        outputs=[flashcard_display, cards_state, index_state, flipped_state, progress_display],
    )


def _render_card(cards: list[dict], idx: int, flipped: bool) -> str:
    """Render a single flashcard with flip support."""
    if not cards or idx >= len(cards):
        return empty_state_html("No Card", "No flashcard to display.", "flashcards")

    card = cards[idx]
    front = card.get("front", "Question")
    back = card.get("back", "Answer")
    topic = card.get("topic", "")

    if flipped:
        bg = "linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(16, 185, 129, 0.08))"
        border = "rgba(34, 197, 94, 0.25)"
        content = back
        label = "📗 Answer"
    else:
        bg = "linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1))"
        border = "rgba(99, 102, 241, 0.25)"
        content = front
        label = "📘 Question"

    return f"""
    <div style="background: {bg}; border: 1px solid {border};
                border-radius: 20px; padding: 40px; min-height: 200px;
                display: flex; flex-direction: column; align-items: center;
                justify-content: center; text-align: center;
                transition: all 0.3s ease; cursor: pointer;">
        <div style="font-size: 12px; color: #6a6a80; margin-bottom: 16px;
                    text-transform: uppercase; letter-spacing: 1px;">
            {label}
        </div>
        <div style="font-size: 20px; line-height: 1.6; color: #e8e8f0; font-weight: 500;
                    max-width: 500px;">
            {content}
        </div>
        <div style="margin-top: 20px; font-size: 12px; color: #6a6a80;">
            {f'📌 {topic}' if topic else ''}
        </div>
    </div>
    """


def _render_progress(idx: int, total: int) -> str:
    """Render progress indicator."""
    if total == 0:
        return ""
    pct = ((idx + 1) / total) * 100
    return f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-top: 12px;">
        <span style="color: #a0a0b8; font-size: 14px; font-weight: 600;">
            Card {idx + 1} of {total}
        </span>
        <div style="flex: 1; height: 6px; background: #16162a; border-radius: 3px; overflow: hidden;">
            <div style="width: {pct:.0f}%; height: 100%; background: linear-gradient(135deg, #6366f1, #8b5cf6);
                        border-radius: 3px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """
