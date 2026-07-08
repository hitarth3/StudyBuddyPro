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

    app = build_app()

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
            )
        elif "empty port" in error_msg.lower():
            print(f"\n❌ Port {settings.port} is already in use.")
            print("   Set STUDYBUDDY_PORT to a different port number.")
            sys.exit(1)
        else:
            raise


if __name__ == "__main__":
    main()
