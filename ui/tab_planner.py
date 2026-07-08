from __future__ import annotations

"""
StudyBuddy Pro — Study Planner Tab

Generates personalized study schedules based on exam date and availability.
"""

import gradio as gr
from datetime import date, timedelta

from backend.study_planner import study_planner
from backend.export_engine import export_engine
from memory.persistence import session_memory
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_planner_tab() -> None:
    """Build the study planner tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📅 Study Planner</h3>
    </div>
    <p style="color: var(--sb-text-secondary); font-size: 14px; margin-bottom: 16px;">
        Generate a personalized study schedule with daily plans, revision timetable, and mock test schedule.
    </p>
    """)

    # Controls
    with gr.Row():
        exam_date = gr.Textbox(
            label="📆 Exam Date (YYYY-MM-DD)",
            placeholder="e.g., 2026-08-15",
            value=(date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            elem_classes=["input-field"],
            scale=1,
        )
        hours_per_day = gr.Slider(
            minimum=1, maximum=12, value=4, step=0.5,
            label="⏰ Study Hours per Day",
            scale=1,
        )

    topics_input = gr.Textbox(
        label="📋 Topics (comma-separated, leave empty to auto-detect)",
        placeholder="e.g., Algebra, Calculus, Statistics",
        elem_classes=["input-field"],
    )

    generate_btn = gr.Button("📅 Generate Study Plan", elem_classes=["primary-btn"])

    # Status
    plan_status = gr.HTML(value="", elem_id="plan-status")

    # Plan display
    plan_display = gr.Markdown(
        value="*Configure your exam details above and generate a personalized study plan.*",
        elem_id="study-plan",
    )

    # Export
    export_btn = gr.Button("💾 Export Study Plan", elem_classes=["secondary-btn"], size="sm")
    export_file = gr.File(label="Download", visible=False)

    # State
    plan_data_state = gr.State(None)

    # Callbacks
    def _generate(exam_dt: str, hours: float, topics_text: str):
        topics = None
        if topics_text.strip():
            topics = [t.strip() for t in topics_text.split(",") if t.strip()]

        result = study_planner.generate_plan(
            exam_date_str=exam_dt,
            hours_per_day=hours,
            topics=topics,
        )

        if "error" in result:
            return (
                f'<span class="badge badge-error">❌ {result["error"]}</span>',
                f'*{result["error"]}*',
                None,
            )

        days = result.get("days_remaining", "?")
        status = (
            f'<span class="badge badge-success">✅ Study plan generated — '
            f'{days} days until exam</span>'
        )

        # Save to memory
        session_memory.add_study_plan(result)

        return status, result.get("plan", ""), result

    def _export(data: dict | None):
        if not data:
            return gr.update(visible=False)
        path = export_engine.export_study_plan(data)
        if path:
            return gr.update(value=path, visible=True)
        return gr.update(visible=False)

    generate_btn.click(
        fn=_generate,
        inputs=[exam_date, hours_per_day, topics_input],
        outputs=[plan_status, plan_display, plan_data_state],
    )

    export_btn.click(
        fn=_export,
        inputs=[plan_data_state],
        outputs=[export_file],
    )
