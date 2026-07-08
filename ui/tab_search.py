from __future__ import annotations

"""
StudyBuddy Pro — Search Tab

Search through uploaded documents by keyword, topic, or document name.
"""

import gradio as gr

from backend.vector_store import vector_store
from ui.components import empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_search_tab() -> None:
    """Build the search tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>🔍 Search Documents</h3>
    </div>
    <p style="color: #a0a0b8; font-size: 14px; margin-bottom: 16px;">
        Search through your uploaded study material by keyword, topic, or document.
    </p>
    """)

    # Search controls
    with gr.Row():
        search_query = gr.Textbox(
            label="Search Query",
            placeholder="Enter a keyword, topic, or question...",
            elem_classes=["input-field"],
            scale=3,
        )
        search_btn = gr.Button("🔍 Search", elem_classes=["primary-btn"], scale=1)

    with gr.Row():
        doc_filter = gr.Dropdown(
            choices=["All Documents"],
            value="All Documents",
            label="Filter by Document",
            scale=1,
            interactive=True,
        )
        num_results = gr.Slider(
            minimum=1, maximum=20, value=5, step=1,
            label="Number of Results",
            scale=1,
        )

    # Results
    search_results = gr.HTML(
        value=empty_state_html(
            "Search Your Notes",
            "Enter a search term to find relevant passages in your uploaded documents.",
            "search"
        ),
        elem_id="search-results",
    )

    # Refresh document list button
    refresh_docs_btn = gr.Button("🔄 Refresh Document List", size="sm",
                                 elem_classes=["secondary-btn"])

    # Callbacks
    def _search(query: str, doc: str, k: int):
        if not query.strip():
            return empty_state_html("Enter a Query", "Type a search term to find relevant content.", "search")

        doc_name = None if doc == "All Documents" else doc

        results = vector_store.search_by_keyword(query, document=doc_name, k=int(k))

        if not results:
            return empty_state_html(
                "No Results Found",
                f"No matches found for '{query}'. Try different keywords.",
                "search"
            )

        html_parts = [
            f'<div style="color: #a0a0b8; font-size: 13px; margin-bottom: 16px;">'
            f'Found {len(results)} results for "<strong style="color: #e8e8f0;">{query}</strong>"</div>'
        ]

        for i, doc_result in enumerate(results, 1):
            source = doc_result.metadata.get("source", "Unknown")
            page = doc_result.metadata.get("page", "?")
            text = doc_result.page_content

            # Highlight query terms in text
            highlighted = text
            for term in query.lower().split():
                if len(term) > 2:
                    import re
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    highlighted = pattern.sub(
                        f'<mark style="background: rgba(99, 102, 241, 0.25); color: #e8e8f0; '
                        f'padding: 1px 4px; border-radius: 3px;">{term}</mark>',
                        highlighted
                    )

            html_parts.append(f"""
            <div class="source-citation" style="margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #818cf8;">[{i}] {source}</strong>
                    <span class="badge badge-info">Page {page}</span>
                </div>
                <p style="color: #a0a0b8; font-size: 14px; line-height: 1.7; margin: 0;">
                    {highlighted}
                </p>
            </div>
            """)

        return "\n".join(html_parts)

    def _refresh_docs():
        docs = vector_store.get_all_documents()
        choices = ["All Documents"] + docs
        return gr.update(choices=choices, value="All Documents")

    search_btn.click(
        fn=_search,
        inputs=[search_query, doc_filter, num_results],
        outputs=[search_results],
    )

    search_query.submit(
        fn=_search,
        inputs=[search_query, doc_filter, num_results],
        outputs=[search_results],
    )

    refresh_docs_btn.click(
        fn=_refresh_docs,
        outputs=[doc_filter],
    )
