from __future__ import annotations

"""
StudyBuddy Pro — Revision Notes Tab

Generates comprehensive revision notes with definitions, formulas, and exam tips.
"""

import gradio as gr

from backend.summary_engine import summary_engine
from backend.export_engine import export_engine
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_revision_tab() -> None:
    """Build the revision notes tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📚 Revision Notes</h3>
    </div>
    <p style="color: var(--sb-text-secondary); font-size: 14px; margin-bottom: 16px;">
        Generate comprehensive revision notes with definitions, formulas, examples, and exam tips.
    </p>
    """)

    # Controls
    with gr.Row():
        rev_topic = gr.Textbox(
            label="Topic Focus",
            placeholder="e.g., Chapter 3, Neural Networks, All Topics",
            value="all topics",
            elem_classes=["input-field"],
            scale=3,
        )
        generate_btn = gr.Button("📚 Generate Revision Notes",
                                 elem_classes=["primary-btn"], scale=1)

    # Status
    rev_status = gr.HTML(value="", elem_id="rev-status")

    # Notes display
    notes_display = gr.Markdown(
        value="*Generate revision notes from your uploaded material to see them here.*",
        elem_id="revision-notes",
    )

    # Export
    export_btn = gr.Button("💾 Export as Markdown", elem_classes=["secondary-btn"], size="sm")
    export_file = gr.File(label="Download", visible=False)

    # State
    notes_data_state = gr.State(None)

    # Callbacks
    def _generate(topic: str):
        result = summary_engine.generate_revision_notes(topic=topic)
        if "error" in result:
            return (
                f'<span class="badge badge-error">❌ {result["error"]}</span>',
                f'*{result["error"]}*',
                None,
            )
        return (
            '<span class="badge badge-success">✅ Revision notes generated</span>',
            result.get("notes", ""),
            result,
        )

    def _export(data: dict | None):
        if not data:
            return gr.update(visible=False)
        path = export_engine.export_revision_notes(data)
        if path:
            return gr.update(value=path, visible=True)
        return gr.update(visible=False)

    generate_btn.click(
        fn=_generate,
        inputs=[rev_topic],
        outputs=[rev_status, notes_display, notes_data_state],
    )

    export_btn.click(
        fn=_export,
        inputs=[notes_data_state],
        outputs=[export_file],
    )
