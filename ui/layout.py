from __future__ import annotations

"""
StudyBuddy Pro — Main Layout

Assembles the complete Gradio Blocks interface with header, tabs, and all pages.
Simplifies tab structure to: Dashboard, Upload, Chat, Quiz, Flashcards, Summary, Revision.
Adds manual Dark/Light mode toggle in the header.
"""

import gradio as gr

from ui.theme import get_theme
from ui.css import CUSTOM_CSS
from ui.tab_dashboard import create_dashboard_tab
from ui.tab_upload import create_upload_tab
from ui.tab_chat import create_chat_tab
from ui.tab_quiz import create_quiz_tab
from ui.tab_flashcards import create_flashcards_tab
from ui.tab_revision import create_revision_tab
from ui.tab_summary import create_summary_tab
from config.settings import settings
from utils.logger import get_logger

log = get_logger(__name__)

# Force dark mode via JS if no theme is specified in URL and set button emoji
_DARK_MODE_JS = """
function() {
    const url = new URL(window.location);
    if (!url.searchParams.get('__theme')) {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
    
    // Set initial toggle button text
    setTimeout(() => {
        const isDark = document.querySelector('.gradio-container')?.classList.contains('dark') || 
                       document.body.classList.contains('dark') ||
                       url.searchParams.get('__theme') === 'dark';
        const themeBtn = document.querySelector('#theme-toggle-btn button') || document.querySelector('#theme-toggle-btn');
        if (themeBtn) {
            themeBtn.innerText = isDark ? '☀️' : '🌙';
        }
    }, 400);
}
"""

_THEME_TOGGLE_JS = """
() => {
    const container = document.querySelector('.gradio-container');
    const body = document.body;
    const themeBtn = document.querySelector('#theme-toggle-btn button') || document.querySelector('#theme-toggle-btn');
    
    if (container) {
        container.classList.toggle('dark');
        body.classList.toggle('dark');
        const isDark = container.classList.contains('dark');
        if (themeBtn) {
            themeBtn.innerText = isDark ? '☀️' : '🌙';
        }
        const url = new URL(window.location);
        url.searchParams.set('__theme', isDark ? 'dark' : 'light');
        window.history.replaceState({}, '', url.toString());
    } else {
        body.classList.toggle('dark');
        document.documentElement.classList.toggle('dark');
        const isDark = body.classList.contains('dark');
        if (themeBtn) {
            themeBtn.innerText = isDark ? '☀️' : '🌙';
        }
        const url = new URL(window.location);
        url.searchParams.set('__theme', isDark ? 'dark' : 'light');
        window.history.replaceState({}, '', url.toString());
    }
}
"""


def build_app() -> gr.Blocks:
    """Build and return the complete Gradio application."""

    theme = get_theme()

    with gr.Blocks(
        theme=theme,
        css=CUSTOM_CSS,
        js=_DARK_MODE_JS,
        title="StudyBuddy Pro — AI Study Assistant",
        analytics_enabled=False,
    ) as app:

        # --- Header ---
        with gr.Row(elem_classes=["app-header"]):
            with gr.Column(scale=3, elem_classes=["header-brand"]):
                gr.HTML("""
                <div style="margin-bottom: 0;">
                    <h1 style="font-size: 28px !important; font-weight: 800 !important; background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 !important; letter-spacing: -0.5px;">✨ StudyBuddy Pro</h1>
                    <p style="color: var(--sb-text-secondary) !important; font-size: 14px !important; margin: 4px 0 0 0 !important;">AI-Powered Study Assistant • Transform your notes into mastery</p>
                </div>
                """)
            with gr.Column(scale=3, min_width=320, elem_classes=["header-actions"]):
                with gr.Row(equal_height=True, elem_classes=["header-actions"]):
                    # Light/Dark mode toggle button
                    with gr.Column(scale=1, min_width=72):
                        theme_btn = gr.Button("☀️", elem_id="theme-toggle-btn", elem_classes=["secondary-btn"], size="sm", scale=1)
                    with gr.Column(scale=4, min_width=240):
                        model_selector = gr.Dropdown(
                            choices=[
                                ("Llama 3.3 70B (Versatile)", "llama-3.3-70b-versatile"),
                                ("Llama 3.1 8B (Fast, High Rate Limits)", "llama-3.1-8b-instant"),
                                ("Gemma 2 9B (Creative)", "gemma2-9b-it"),
                            ],
                            value=settings.llm_model,
                            label="🧠 Model",
                            interactive=True,
                            container=True,
                            elem_classes=["input-field", "header-model-select"],
                            scale=1,
                        )

        def change_model(new_model):
            settings.llm_model = new_model
            # Reset lazy-loaded LLM instances
            from backend.rag_engine import rag_engine
            from backend.quiz_engine import quiz_engine
            from backend.flashcard_engine import flashcard_engine
            from backend.summary_engine import summary_engine
            from backend.study_planner import study_planner

            rag_engine._llm = None
            quiz_engine._llm = None
            flashcard_engine._llm = None
            summary_engine._llm = None
            study_planner._llm = None
            log.info("Active LLM switched to: %s", new_model)

        model_selector.change(fn=change_model, inputs=model_selector)
        theme_btn.click(None, None, None, js=_THEME_TOGGLE_JS)

        # --- Tabbed Navigation ---
        with gr.Tabs() as tabs:
            with gr.Tab("🏠 Dashboard", id="dashboard"):
                create_dashboard_tab()

            with gr.Tab("📤 Upload", id="upload"):
                create_upload_tab()

            with gr.Tab("💬 AI Chat", id="chat"):
                create_chat_tab()

            with gr.Tab("📝 Quiz", id="quiz"):
                create_quiz_tab()

            with gr.Tab("🃏 Flashcards", id="flashcards"):
                create_flashcards_tab()

            with gr.Tab("📄 Summary", id="summary"):
                create_summary_tab()

            with gr.Tab("📚 Revision", id="revision"):
                create_revision_tab()

        # --- Footer ---
        gr.HTML("""
        <div style="text-align: center; padding: 24px; margin-top: 32px;
                    border-top: 1px solid #2a2a45; color: #6a6a80; font-size: 13px;">
            <p>StudyBuddy Pro v1.0 • Built with ❤️ using Gradio, LangChain & Groq</p>
            <p style="margin-top: 4px;">Powered by Llama 3.3 70B • HuggingFace Embeddings • ChromaDB</p>
        </div>
        """)

    log.info("Application UI built successfully")
    return app
