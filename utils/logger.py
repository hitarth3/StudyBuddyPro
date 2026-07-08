"""
StudyBuddy Pro — Logging Configuration

Provides a configured logger with console and file handlers,
log rotation, and structured formatting.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


_LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str = "studybuddy") -> logging.Logger:
    """Get or create a named logger with console + rotating file handlers."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (INFO+)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (DEBUG+, 5 MB rotation, keep 3 backups)
    fh = RotatingFileHandler(
        _LOG_DIR / "studybuddy.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
