from __future__ import annotations

"""
StudyBuddy Pro — Upload Tab

Document upload with progress tracking and file management.
"""

import gradio as gr

from backend.document_processor import document_processor, DocumentProcessingError
from backend.vector_store import vector_store
from memory.persistence import session_memory
from ui.components import file_info_html, empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_upload_tab() -> None:
    """Build the upload tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📤 Upload Study Material</h3>
    </div>
    """)

    gr.HTML("""
    <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;">
        <span class="badge badge-primary">PDF</span>
        <span class="badge badge-primary">DOCX</span>
        <span class="badge badge-primary">TXT</span>
        <span style="color: var(--sb-text-muted); font-size: 13px; display: flex; align-items: center;">
            Max 50MB per file
        </span>
    </div>
    """)

    # Upload area
    file_upload = gr.File(
        label="Drop files here or click to browse",
        file_count="multiple",
        file_types=[".pdf", ".docx", ".txt"],
        elem_classes=["upload-area"],
    )

    # Status message
    upload_status = gr.HTML(value="", elem_id="upload-status")

    # File list
    gr.HTML("""
    <div class="section-header" style="margin-top: 24px;">
        <h3>📁 Uploaded Documents</h3>
    </div>
    """)

    file_list_display = gr.HTML(
        value=_render_file_list(),
        elem_id="file-list",
    )

    # Vector store stats
    store_stats = gr.HTML(value=_render_store_stats(), elem_id="store-stats")

    # Delete all button
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh", elem_classes=["secondary-btn"], size="sm")
        delete_all_btn = gr.Button("🗑️ Clear All Documents", elem_classes=["secondary-btn"],
                                   size="sm", variant="stop")

    # Wire callbacks
    file_upload.upload(
        fn=_handle_upload,
        inputs=[file_upload],
        outputs=[upload_status, file_list_display, store_stats],
    )

    refresh_btn.click(
        fn=_refresh_all,
        outputs=[file_list_display, store_stats],
    )

    delete_all_btn.click(
        fn=_delete_all,
        outputs=[upload_status, file_list_display, store_stats],
    )


def _handle_upload(files) -> tuple[str, str, str]:
    """Process uploaded files."""
    if not files:
        return (
            '<span class="badge badge-warning">⚠️ No files selected</span>',
            _render_file_list(),
            _render_store_stats(),
        )

    results = []
    errors = []

    for file in files:
        file_path = file.name if hasattr(file, 'name') else str(file)
        original_name = file_path.split("/")[-1].split("\\")[-1]

        try:
            # Check if already uploaded
            existing = session_memory.get_uploaded_files()
            if any(f.get("name") == original_name for f in existing):
                results.append(f"⏭️ '{original_name}' already uploaded, skipping.")
                continue

            # Process document
            chunks, file_info = document_processor.process_file(
                file_path, original_name=original_name
            )

            # Add to vector store
            vector_store.add_documents(chunks)

            # Save to memory
            session_memory.add_uploaded_file(file_info)

            results.append(
                f'✅ <strong>{original_name}</strong> — '
                f'{file_info["pages"]} pages, {file_info["chunks"]} chunks'
            )

        except DocumentProcessingError as e:
            errors.append(f'❌ <strong>{original_name}</strong>: {str(e)}')
            log.warning("Upload failed for %s: %s", original_name, e)
        except Exception as e:
            errors.append(f'❌ <strong>{original_name}</strong>: Unexpected error — {str(e)[:100]}')
            log.exception("Unexpected upload error for %s", original_name)

    # Build status HTML
    status_parts = []
    if results:
        status_parts.append(
            '<div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2); '
            'border-radius: 12px; padding: 16px; margin: 8px 0;">'
            + "<br>".join(results) + '</div>'
        )
    if errors:
        status_parts.append(
            '<div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); '
            'border-radius: 12px; padding: 16px; margin: 8px 0;">'
            + "<br>".join(errors) + '</div>'
        )

    return (
        "\n".join(status_parts),
        _render_file_list(),
        _render_store_stats(),
    )


def _render_file_list() -> str:
    """Render the uploaded files list."""
    files = session_memory.get_uploaded_files()
    return file_info_html(files)


def _render_store_stats() -> str:
    """Render vector store statistics."""
    stats = vector_store.get_stats()
    return f"""
    <div style="background: var(--sb-bg-card); border: 1px solid var(--sb-border); border-radius: 12px;
                padding: 16px; margin-top: 16px;">
        <div style="display: flex; gap: 24px; flex-wrap: wrap;">
            <div>
                <span style="color: var(--sb-text-muted); font-size: 12px;">Total Documents</span>
                <div style="color: var(--sb-text-primary); font-weight: 700; font-size: 20px;">{stats['total_documents']}</div>
            </div>
            <div>
                <span style="color: var(--sb-text-muted); font-size: 12px;">Total Chunks</span>
                <div style="color: var(--sb-text-primary); font-weight: 700; font-size: 20px;">{stats['total_chunks']}</div>
            </div>
            <div>
                <span style="color: var(--sb-text-muted); font-size: 12px;">Status</span>
                <div style="font-size: 14px;">
                    {'<span class="badge badge-success">Ready</span>' if stats['total_chunks'] > 0
                     else '<span class="badge badge-warning">Empty</span>'}
                </div>
            </div>
        </div>
    </div>
    """


def _refresh_all() -> tuple[str, str]:
    """Refresh file list and stats."""
    return _render_file_list(), _render_store_stats()


def _delete_all() -> tuple[str, str, str]:
    """Delete all documents and reset."""
    files = session_memory.get_uploaded_files()
    for f in files:
        vector_store.delete_document(f.get("name", ""))
        session_memory.remove_uploaded_file(f.get("name", ""))

    return (
        '<span class="badge badge-info">🗑️ All documents cleared</span>',
        _render_file_list(),
        _render_store_stats(),
    )
