"""
StudyBuddy Pro — Application Entry Point

Launch the complete AI-powered study assistant.

Usage:
    python app.py

Environment:
    GROQ_API_KEY: Required. Get one at https://console.groq.com/
"""

import sys
from pathlib import Path

# Configure UTF-8 encoding for standard streams to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on the Python path
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv

# Monkeypatch gradio_client to prevent TypeError: argument of type 'bool' is not iterable
try:
    from gradio_client import utils as gradio_client_utils
    _orig = gradio_client_utils._json_schema_to_python_type
    def _patched(schema, defs):
        if not isinstance(schema, dict):
            if isinstance(schema, bool):
                return "bool"
            return "Any"
        return _orig(schema, defs)
    gradio_client_utils._json_schema_to_python_type = _patched
except Exception:
    pass

# Monkeypatch gradio.routes.toorjson to clean surrogate characters which crash orjson
try:
    import gradio.routes
    _orig_toorjson = gradio.routes.toorjson

    def clean_surrogates(obj, path=""):
        if isinstance(obj, str):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in obj):
                cleaned = "".join(c if not (0xD800 <= ord(c) <= 0xDFFF) else '\uFFFD' for c in obj)
                print(f"[SURROGATE DETECTED] at {path}: {repr(obj)} -> {repr(cleaned)}")
                return cleaned
            return obj
        elif isinstance(obj, dict):
            return {clean_surrogates(k, f"{path}.{k}"): clean_surrogates(v, f"{path}.{k}") for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_surrogates(x, f"{path}[{i}]") for i, x in enumerate(obj)]
        elif isinstance(obj, tuple):
            return tuple(clean_surrogates(x, f"{path}[{i}]") for i, x in enumerate(obj))
        return obj

    def _patched_toorjson(value):
        return _orig_toorjson(clean_surrogates(value))

    gradio.routes.toorjson = _patched_toorjson
    if hasattr(gradio.routes, "templates") and hasattr(gradio.routes.templates, "env"):
        gradio.routes.templates.env.filters["toorjson"] = _patched_toorjson
except Exception as e:
    print(f"Failed to patch gradio.routes.toorjson: {e}")

# Load .env file if it exists
load_dotenv(_PROJECT_ROOT / ".env")

from config.settings import settings
from utils.logger import get_logger

log = get_logger("studybuddy.main")


def main() -> None:
    """Validate configuration and launch the application."""
    print("\n" + "=" * 60)
    print("  ✨  StudyBuddy Pro — AI Study Assistant  ✨")
    print("=" * 60 + "\n")

    # Validate settings
    errors = settings.validate()
    if errors:
        print("❌ Configuration errors:\n")
        for e in errors:
            print(f"   • {e}")
        print("\n💡 Tip: Copy .env.example to .env and set your GROQ_API_KEY")
        print("   Get one at: https://console.groq.com/\n")
        sys.exit(1)

    # Create data directories
    settings.ensure_directories()
    log.info("Data directories ready at: %s", settings.data_dir)

    # Build and launch
    print("🔧 Building application...")
    from ui.layout import build_app
    from ui.css import CUSTOM_CSS
    from ui.layout import _DARK_MODE_JS

    app, theme = build_app()

    print(f"\n🚀 Launching StudyBuddy Pro")
    print(f"   Host: {settings.host}")
    print(f"   Port: {settings.port}")
    print(f"   URL:  http://localhost:{settings.port}")
    print(f"\n   Press Ctrl+C to stop\n")

    try:
        app.launch(
            server_name=settings.host,
            server_port=settings.port,
            share=settings.share,
            show_error=True,
            show_api=False,
            theme=theme,
            css=CUSTOM_CSS,
            js=_DARK_MODE_JS,
        )
    except (ValueError, OSError) as e:
        error_msg = str(e)
        if "shareable link" in error_msg or "localhost" in error_msg.lower():
            print("\n⚠️  Localhost not accessible — retrying with share=True...")
            app.launch(
                server_name=settings.host,
                server_port=settings.port,
                share=True,
                show_error=True,
                show_api=False,
                theme=theme,
                css=CUSTOM_CSS,
                js=_DARK_MODE_JS,
            )
        elif "empty port" in error_msg.lower():
            print(f"\n❌ Port {settings.port} is already in use.")
            print("   Set STUDYBUDDY_PORT to a different port number.")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main()
