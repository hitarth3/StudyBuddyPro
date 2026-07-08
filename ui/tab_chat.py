from __future__ import annotations

"""
StudyBuddy Pro — Chat Tab

AI chat interface with RAG pipeline, source citations, and explain modes.
"""

import gradio as gr

from backend.rag_engine import rag_engine
from memory.persistence import session_memory
from ui.components import source_citation_html, confidence_badge_html, empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_chat_tab() -> None:
    """Build the AI chat tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>💬 AI Study Assistant</h3>
    </div>
    """)

    # Controls row
    with gr.Row():
        explain_mode = gr.Dropdown(
            choices=[
                ("Default", "default"),
                ("Explain like I'm 10", "eli10"),
                ("High School", "high_school"),
                ("College / University", "college"),
                ("Exam Revision", "exam_revision"),
            ],
            value="default",
            label="🎓 Explain Mode",
            scale=1,
        )
        difficulty = gr.Dropdown(
            choices=[
                ("Easy", "easy"),
                ("Medium", "medium"),
                ("Hard", "hard"),
                ("Adaptive", "adaptive"),
            ],
            value="medium",
            label="📊 Difficulty",
            scale=1,
        )

    # Chat area
    chatbot = gr.Chatbot(
        value=[],
        height=480,
        elem_classes=["chatbot"],
        show_label=False,
        bubble_full_width=False,
        avatar_images=(None, None),
        type="messages",
    )

    # Input area
    with gr.Row():
        msg_input = gr.Textbox(
            placeholder="Ask anything about your study material...",
            show_label=False,
            scale=6,
            elem_classes=["input-field"],
            lines=1,
            max_lines=3,
        )
        send_btn = gr.Button("Send ➤", elem_classes=["primary-btn"], scale=1)

    # Suggested questions
    gr.HTML("""
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
        <span style="color: #6a6a80; font-size: 12px; display: flex; align-items: center;">💡 Try:</span>
    </div>
    """)
    with gr.Row():
        q1 = gr.Button("Summarize the key concepts", size="sm", elem_classes=["secondary-btn"])
        q2 = gr.Button("What are the main topics?", size="sm", elem_classes=["secondary-btn"])
        q3 = gr.Button("Explain the most important formula", size="sm", elem_classes=["secondary-btn"])

    # Source citations panel
    with gr.Accordion("📎 Source Citations", open=False):
        citations_display = gr.HTML(
            value=empty_state_html("No Citations Yet", "Ask a question to see source citations.", "search"),
            elem_id="citations-panel",
        )

    # Confidence display
    confidence_display = gr.HTML(value="", elem_id="confidence-display")

    # Clear chat button
    clear_btn = gr.Button("🗑️ Clear Chat", size="sm", elem_classes=["secondary-btn"])

    # --- State ---
    chat_state = gr.State([])  # Internal chat history for RAG

    # --- Callbacks ---
    def _send_message(message: str, history: list, rag_history: list,
                      mode: str, diff: str):
        """Process a message through the RAG pipeline."""
        if not message.strip():
            return history, rag_history, "", "", ""

        # Add user message to display
        history = history + [{"role": "user", "content": message}]

        # Call RAG engine
        result = rag_engine.ask(
            question=message,
            chat_history=rag_history,
            explain_mode=mode,
            difficulty=diff,
        )

        answer = result.get("answer", "Sorry, I couldn't generate a response.")
        sources = result.get("sources", [])
        confidence = result.get("confidence", 0)

        # Add to history
        history = history + [{"role": "assistant", "content": answer}]

        # Update RAG history
        rag_history = rag_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]

        # Keep last N turns
        rag_history = rag_history[-20:]

        # Save to memory
        session_memory.add_chat_message("user", message)
        session_memory.add_chat_message("assistant", answer, sources)

        # Build citations and confidence HTML
        citations_html = source_citation_html(sources)
        if not citations_html:
            citations_html = empty_state_html("No Sources", "No relevant sources found.", "info")

        confidence_html = confidence_badge_html(confidence) if confidence > 0 else ""

        return history, rag_history, "", citations_html, confidence_html

    def _quick_question(question: str, history: list, rag_history: list,
                        mode: str, diff: str):
        """Handle quick question button clicks."""
        return _send_message(question, history, rag_history, mode, diff)

    def _clear_chat():
        """Clear chat history."""
        session_memory.clear_chat_history()
        return [], [], empty_state_html("Chat Cleared", "Ask a question to start a new conversation.", "chat"), ""

    # Wire events
    send_inputs = [msg_input, chatbot, chat_state, explain_mode, difficulty]
    send_outputs = [chatbot, chat_state, msg_input, citations_display, confidence_display]

    send_btn.click(fn=_send_message, inputs=send_inputs, outputs=send_outputs)
    msg_input.submit(fn=_send_message, inputs=send_inputs, outputs=send_outputs)

    for btn, question in [(q1, "Summarize the key concepts"),
                          (q2, "What are the main topics covered?"),
                          (q3, "Explain the most important formula")]:
        btn.click(
            fn=_quick_question,
            inputs=[gr.State(question), chatbot, chat_state, explain_mode, difficulty],
            outputs=send_outputs,
        )

    clear_btn.click(
        fn=_clear_chat,
        outputs=[chatbot, chat_state, citations_display, confidence_display],
    )
