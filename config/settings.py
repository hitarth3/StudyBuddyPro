from __future__ import annotations

"""
StudyBuddy Pro — Centralized Configuration

All configurable settings in one place. Reads from environment variables
with sensible defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """Application-wide settings."""

    # --- Groq LLM ---
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 4096
    llm_timeout: int = 60
    llm_max_retries: int = 2

    # --- Embedding ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    # --- Chunking ---
    chunk_size: int = 500
    chunk_overlap: int = 100

    # --- Retrieval ---
    retrieval_k: int = 5
    retrieval_search_type: str = "mmr"
    confidence_threshold: float = 0.60

    # --- Paths ---
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
    data_dir: Path = field(init=False)
    chroma_dir: Path = field(init=False)
    uploads_dir: Path = field(init=False)
    sessions_dir: Path = field(init=False)
    exports_dir: Path = field(init=False)

    # --- Server ---
    host: str = "127.0.0.1"
    port: int = 7860
    share: bool = False

    # --- App ---
    app_name: str = "StudyBuddy Pro"
    app_version: str = "1.0.0"
    max_file_size_mb: int = 50
    max_chat_history: int = 10
    quiz_mcq_count: int = 5
    quiz_short_count: int = 5
    flashcard_default_count: int = 10

    def __post_init__(self) -> None:
        """Resolve paths and load env overrides."""
        # Load env overrides
        self.groq_api_key = os.getenv("GROQ_API_KEY", self.groq_api_key)
        self.host = os.getenv("STUDYBUDDY_HOST", self.host)
        self.port = int(os.getenv("STUDYBUDDY_PORT", str(self.port)))
        self.share = os.getenv("STUDYBUDDY_SHARE", "false").lower() == "true"

        data_override = os.getenv("STUDYBUDDY_DATA_DIR", "")
        if data_override:
            self.data_dir = Path(data_override).resolve()
        else:
            self.data_dir = self.project_root / "data"

        self.chroma_dir = self.data_dir / "chroma_db"
        self.uploads_dir = self.data_dir / "uploads"
        self.sessions_dir = self.data_dir / "sessions"
        self.exports_dir = self.data_dir / "exports"

    def ensure_directories(self) -> None:
        """Create all required data directories."""
        for d in (self.data_dir, self.chroma_dir, self.uploads_dir,
                  self.sessions_dir, self.exports_dir):
            d.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """Return a list of validation errors (empty = valid)."""
        errors: list[str] = []
        if not self.groq_api_key or self.groq_api_key == "your_groq_api_key_here":
            errors.append(
                "GROQ_API_KEY is not set. Please set it in your environment "
                "or in a .env file. Get one at https://console.groq.com/"
            )
        return errors


# Singleton instance
settings = Settings()
