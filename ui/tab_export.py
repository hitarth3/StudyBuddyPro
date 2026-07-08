from __future__ import annotations

"""
StudyBuddy Pro — Export Tab

Central hub for exporting all study materials.
"""

import gradio as gr

from backend.export_engine import export_engine
from backend.quiz_engine import quiz_engine
from memory.persistence import session_memory
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_export_tab() -> None:
    """Build the export tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>💾 Export Center</h3>
    </div>
    <p style="color: var(--sb-text-secondary); font-size: 14px; margin-bottom: 16px;">
        Export your quizzes, flashcards, study plans, and revision notes as Markdown files.
    </p>
    """)

    # Export options
    with gr.Row(equal_height=True):
        # Quiz export
        with gr.Column():
            gr.HTML("""
            <div style="background: var(--sb-bg-card); border: 1px solid var(--sb-border); border-radius: 16px; padding: 24px;">
                <div style="font-size: 28px; margin-bottom: 8px;">📝</div>
                <h4 style="color: var(--sb-text-primary); margin-bottom: 8px;">Quiz History</h4>
                <p style="color: var(--sb-text-secondary); font-size: 13px;">Export all your past quizzes with answers and explanations.</p>
            </div>
            """)
            export_quiz_btn = gr.Button("Export Quizzes", elem_classes=["secondary-btn"], size="sm")
            quiz_file = gr.File(label="Download", visible=False)

        # Flashcards export
        with gr.Column():
            gr.HTML("""
            <div style="background: var(--sb-bg-card); border: 1px solid var(--sb-border); border-radius: 16px; padding: 24px;">
                <div style="font-size: 28px; margin-bottom: 8px;">🃏</div>
                <h4 style="color: var(--sb-text-primary); margin-bottom: 8px;">Flashcard Sets</h4>
                <p style="color: var(--sb-text-secondary); font-size: 13px;">Export your generated flashcard sets for offline review.</p>
            </div>
            """)
            export_fc_btn = gr.Button("Export Flashcards", elem_classes=["secondary-btn"], size="sm")
            fc_file = gr.File(label="Download", visible=False)

        # Study plans export
        with gr.Column():
            gr.HTML("""
            <div style="background: var(--sb-bg-card); border: 1px solid var(--sb-border); border-radius: 16px; padding: 24px;">
                <div style="font-size: 28px; margin-bottom: 8px;">📅</div>
                <h4 style="color: var(--sb-text-primary); margin-bottom: 8px;">Study Plans</h4>
                <p style="color: var(--sb-text-secondary); font-size: 13px;">Export your personalized study schedules.</p>
            </div>
            """)
            export_plan_btn = gr.Button("Export Plans", elem_classes=["secondary-btn"], size="sm")
            plan_file = gr.File(label="Download", visible=False)

    # Export status
    export_status = gr.HTML(value="", elem_id="export-status")

    # Export history
    gr.HTML("""
    <div class="section-header" style="margin-top: 24px;">
        <h3>📋 Export Summary</h3>
    </div>
    """)
    export_summary = gr.HTML(value=_render_export_summary(), elem_id="export-summary")

    # Callbacks
    def _export_quizzes():
        history = session_memory.get_quiz_history()
        if not history:
            return gr.update(visible=False), '<span class="badge badge-warning">⚠️ No quiz history to export</span>'

        # Export the latest quiz
        latest = history[-1]
        # Build a quiz_data format for export
        quiz_data = {
            "topic": latest.get("topic", "General"),
            "difficulty": latest.get("difficulty", "medium"),
            "questions": latest.get("results", []),
        }
        path = export_engine.export_quiz(quiz_data)
        if path:
            return gr.update(value=path, visible=True), '<span class="badge badge-success">✅ Quiz exported</span>'
        return gr.update(visible=False), '<span class="badge badge-error">❌ Export failed</span>'

    def _export_flashcards():
        sets = session_memory.get_flashcard_sets()
        if not sets:
            return gr.update(visible=False), '<span class="badge badge-warning">⚠️ No flashcard sets to export</span>'

        latest = sets[-1]
        path = export_engine.export_flashcards(latest)
        if path:
            return gr.update(value=path, visible=True), '<span class="badge badge-success">✅ Flashcards exported</span>'
        return gr.update(visible=False), '<span class="badge badge-error">❌ Export failed</span>'

    def _export_plans():
        plans = session_memory.get_study_plans()
        if not plans:
            return gr.update(visible=False), '<span class="badge badge-warning">⚠️ No study plans to export</span>'

        latest = plans[-1]
        path = export_engine.export_study_plan(latest)
        if path:
            return gr.update(value=path, visible=True), '<span class="badge badge-success">✅ Study plan exported</span>'
        return gr.update(visible=False), '<span class="badge badge-error">❌ Export failed</span>'

    export_quiz_btn.click(fn=_export_quizzes, outputs=[quiz_file, export_status])
    export_fc_btn.click(fn=_export_flashcards, outputs=[fc_file, export_status])
    export_plan_btn.click(fn=_export_plans, outputs=[plan_file, export_status])


def _render_export_summary() -> str:
    """Render what's available for export."""
    quizzes = len(session_memory.get_quiz_history())
    flashcards = len(session_memory.get_flashcard_sets())
    plans = len(session_memory.get_study_plans())

    if quizzes == 0 and flashcards == 0 and plans == 0:
        return empty_state_html(
            "Nothing to Export Yet",
            "Generate quizzes, flashcards, or study plans first.",
            "export"
        )

    return f"""
    <div style="display: flex; gap: 16px; flex-wrap: wrap;">
        <div class="badge badge-primary">📝 {quizzes} Quiz{'es' if quizzes != 1 else ''}</div>
        <div class="badge badge-primary">🃏 {flashcards} Flashcard Set{'s' if flashcards != 1 else ''}</div>
        <div class="badge badge-primary">📅 {plans} Study Plan{'s' if plans != 1 else ''}</div>
    </div>
    """
