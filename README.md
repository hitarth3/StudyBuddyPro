# ✨ StudyBuddy Pro — AI-Powered Study Assistant

StudyBuddy Pro is a premium, SaaS-grade local web application designed to transform raw study notes (PDFs, DOCX, TXT) into an interactive, AI-driven learning experience. It leverages high-speed models via Groq, HuggingFace embeddings, and ChromaDB to act as a personal tutor, study tracker, and exam preparation tool.

---

## 🚀 Key Features

*   **📊 Interactive Learning Dashboard**: Track study metrics, streaks, quizzes taken, average scores, weak topics, and active documents. Includes daily study intensity calendars and topic accuracy bar charts.
*   **📤 Upload & Document Processing**: Upload PDFs, DOCX, or TXT documents. Documents are parsed, chunked, and vectorized locally using ChromaDB.
*   **💬 AI RAG Chat (With Source Citations)**: Query your documents with high-precision retrieval. Answers feature source citations (document name, page number) and interactive model switches.
*   **📝 AI Quiz Generator**: Automatically generate custom quizzes (MCQ & Short Answer) focused on specific topics and difficulty levels. Features interactive answer evaluation with detailed explanations and auto-saves results.
*   **🃏 Flashcards Generator**: Generate dynamic flashcards directly from your notes. Cycle through, flip, and study key concepts offline.
*   **📄 AI Summary Generator**: Generate summaries of your materials in various formats (Short, Detailed, or Markdown-formatted Mind Map).
*   **📚 Revision Notes**: Extract formulas, rules, worked examples, mock test schedules, and common mistakes to avoid from your files.
*   **💾 Export Center**: Export your chat summaries, quizzes, flashcards, and revision notes to Markdown files for offline use.
*   **🌗 Premium Dark/Light Theme**: Sleek glassmorphism header UI with manual Dark/Light toggles that persist across page loads and dynamically sync text and component contrast.

---

## 🛠️ Technology Stack

*   **Frontend**: Gradio (Custom CSS/JS, custom components)
*   **LLM Pipeline**: LangChain & LangChain-Groq (Supports Llama 3.3 70B, Llama 3.1 8B, Gemma 2 9B)
*   **Embeddings**: LangChain-HuggingFace (`sentence-transformers/all-MiniLM-L6-v2` running on CPU/GPU)
*   **Vector Store**: LangChain-Chroma & ChromaDB
*   **Document Parsing**: PyMuPDF (`fitz`), `python-docx`
*   **Data Visualization**: Plotly
*   **Session State**: JSON-based thread-safe persistence layer

---

## 📁 Directory Structure

```
StudyBuddyPro/
├── backend/                  # Python back-end logical layers
│   ├── document_processor.py # PDF/DOCX/TXT parsers and text splitters
│   ├── export_engine.py      # MD exporters for quizzes/flashcards/plans
│   ├── flashcard_engine.py   # Flashcard generation logic via LLM
│   ├── quiz_engine.py        # MCQ and Short-Answer generation/grading
│   ├── rag_engine.py         # Retrieval-Augmented Generation pipeline
│   ├── study_planner.py      # Automated study plan scheduler
│   ├── summary_engine.py     # Summary and Mind-Map formatting
│   └── vector_store.py       # ChromaDB vector store wrapper
├── config/                   # Centralized configuration settings
│   └── settings.py
├── data/                     # Local storage directories (Auto-created)
│   ├── chroma_db/            # ChromaDB database index files
│   ├── exports/              # Generated markdown export files
│   ├── logs/                 # Rolling execution logs
│   ├── sessions/             # JSON session storage (session.json)
│   └── uploads/              # Stored uploaded files
├── memory/                   # Session persistence module
│   └── persistence.py
├── ui/                       # Front-end user interface
│   ├── css.py                # Core responsive CSS variables & overrides
│   ├── layout.py             # Main blocks assembly and theme scripts
│   ├── theme.py              # Custom Gradio StudyBuddy theme definition
│   └── tab_*.py              # Modular tab implementations
├── utils/                    # Shared helper and logging utilities
│   ├── helpers.py
│   └── logger.py
├── app.py                    # Entry point script
├── requirements.txt          # Python packages list
└── README.md
```

---

## ⚙️ Prerequisites & Setup

### 1. Clone & Navigate
Ensure you are in the project folder:
```bash
cd StudyBuddyPro
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` (or create a `.env` file manually in the root directory) and set your **Groq API Key**:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
> Get a free Groq API key at [console.groq.com](https://console.groq.com/).

### 3. Launching the App
The workspace includes a Python virtual environment. Always execute commands using this environment to ensure all dependencies are resolved.

*   **Windows**:
    ```powershell
    ..\Scripts\python.exe app.py
    ```

*   **Unix / MacOS**:
    ```bash
    ../bin/python app.py
    ```

Once loaded, open your browser and navigate to:
**`http://localhost:7860/`**

---

## ⚙️ Custom Port Configurations

By default, the server runs on port `7860`. If this port is occupied, set the `STUDYBUDDY_PORT` environment variable before running:

*   **Windows (PowerShell)**:
    ```powershell
    $env:STUDYBUDDY_PORT="7861"
    ..\Scripts\python.exe app.py
    ```
*   **Unix / MacOS**:
    ```bash
    STUDYBUDDY_PORT=7861 ../bin/python app.py
    ```