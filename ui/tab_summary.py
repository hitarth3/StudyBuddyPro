from __future__ import annotations

"""
StudyBuddy Pro — Summary Tab

AI-powered summaries in multiple formats: short, detailed, bullets, one-page, mind map.
"""

import gradio as gr

from backend.summary_engine import summary_engine
from backend.export_engine import export_engine
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_summary_tab() -> None:
    """Build the summary tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📄 AI Summary Generator</h3>
    </div>
    <p style="color: #a0a0b8; font-size: 14px; margin-bottom: 16px;">
        Generate summaries of your study material in various formats.
    </p>
    """)

    # Controls
    with gr.Row():
        summary_mode = gr.Dropdown(
            choices=[
                ("📝 Short Summary", "short"),
                ("📖 Detailed Summary", "detailed"),
                ("📋 Bullet Point Notes", "bullets"),
                ("📄 One-Page Study Sheet", "one_page"),
                ("🗺️ Mind Map", "mind_map"),
            ],
            value="short",
            label="Summary Mode",
            scale=1,
        )
        summary_topic = gr.Textbox(
            label="Topic Focus",
            placeholder="e.g., All Topics, Chapter 5",
            value="all topics",
            elem_classes=["input-field"],
            scale=2,
        )
        generate_btn = gr.Button("✨ Generate Summary",
                                 elem_classes=["primary-btn"], scale=1)

    # Status
    summary_status = gr.HTML(value="", elem_id="summary-status")

    # Summary display
    summary_display = gr.Markdown(
        value="*Select a summary mode and generate to see your study material summary.*",
        elem_id="summary-output",
    )

    # Export
    export_btn = gr.Button("💾 Export Summary", elem_classes=["secondary-btn"], size="sm")
    export_file = gr.File(label="Download", visible=False)

    # State
    summary_data_state = gr.State(None)

    # Callbacks
    def _generate(mode: str, topic: str):
        result = summary_engine.generate_summary(mode=mode, topic=topic)
        if "error" in result:
            return (
                f'<span class="badge badge-error">❌ {result["error"]}</span>',
                f'*{result["error"]}*',
                None,
            )

        label = result.get("mode_label", "Summary")
        return (
            f'<span class="badge badge-success">✅ {label} generated</span>',
            result.get("summary", ""),
            result,
        )

    def _export(data: dict | None):
        if not data:
            return gr.update(visible=False)
        path = export_engine.export_summary(data)
        if path:
            return gr.update(value=path, visible=True)
        return gr.update(visible=False)

    generate_btn.click(
        fn=_generate,
        inputs=[summary_mode, summary_topic],
        outputs=[summary_status, summary_display, summary_data_state],
    )

    export_btn.click(
        fn=_export,
        inputs=[summary_data_state],
        outputs=[export_file],
    )
