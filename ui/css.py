"""
StudyBuddy Pro — Custom CSS

Premium SaaS-grade styling with glassmorphism, animations, and responsive design.
"""

CUSTOM_CSS = """
/* ============================================================
   STUDYBUDDY PRO — PREMIUM CSS
   ============================================================ */

/* --- Google Font Import --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* --- Root Variables --- */
:root {
    --sb-accent-primary: #6366f1;
    --sb-accent-secondary: #8b5cf6;
    --sb-accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
    --sb-accent-gradient-hover: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
    --sb-success: #22c55e;
    --sb-warning: #f59e0b;
    --sb-error: #ef4444;
    --sb-info: #3b82f6;
    --sb-radius: 12px;
    --sb-radius-lg: 16px;
    --sb-radius-xl: 20px;
    --sb-transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.gradio-container.dark {
    --sb-bg-primary: #0a0a0f;
    --sb-bg-secondary: #12121a;
    --sb-bg-card: #1a1a2e;
    --sb-bg-card-hover: #1e1e35;
    --sb-bg-input: #16162a;
    --sb-border: #2a2a45;
    --sb-border-light: #3a3a55;
    --sb-text-primary: #e8e8f0;
    --sb-text-secondary: #a0a0b8;
    --sb-text-muted: #6a6a80;
    --sb-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
    --sb-shadow-lg: 0 10px 25px -3px rgba(0, 0, 0, 0.4), 0 4px 10px -4px rgba(0, 0, 0, 0.3);
    --sb-glass: rgba(26, 26, 46, 0.8);
    --sb-glass-border: rgba(99, 102, 241, 0.15);
}

.gradio-container:not(.dark) {
    --sb-bg-primary: #f8fafc;
    --sb-bg-secondary: #f1f5f9;
    --sb-bg-card: #ffffff;
    --sb-bg-card-hover: #f8fafc;
    --sb-bg-input: #f1f5f9;
    --sb-border: #cbd5e1;
    --sb-border-light: #e2e8f0;
    --sb-text-primary: #0f172a;
    --sb-text-secondary: #334155;
    --sb-text-muted: #64748b;
    --sb-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    --sb-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --sb-glass: rgba(255, 255, 255, 0.9);
    --sb-glass-border: rgba(99, 102, 241, 0.1);
}

/* --- Global Reset --- */
.gradio-container {
    background: var(--sb-bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    max-width: 100% !important;
    padding: 0 !important;
}

.gradio-container .main {
    max-width: 100% !important;
}

/* --- App Header --- */
.app-header {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.08), rgba(168, 85, 247, 0.06));
    border-bottom: 1px solid var(--sb-glass-border);
    backdrop-filter: blur(20px);
    padding: 20px 32px;
    margin: -16px -16px 24px -16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.app-header h1 {
    font-size: 28px !important;
    font-weight: 800 !important;
    background: var(--sb-accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 !important;
    letter-spacing: -0.5px;
}

.app-header p {
    color: var(--sb-text-secondary) !important;
    font-size: 14px !important;
    margin: 4px 0 0 0 !important;
}

/* --- Tab Navigation --- */
.tab-nav {
    background: var(--sb-bg-secondary) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius-lg) !important;
    padding: 6px !important;
    margin-bottom: 24px !important;
    display: flex !important;
    gap: 4px !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
}

.tab-nav::-webkit-scrollbar {
    display: none;
}

.tab-nav button {
    background: transparent !important;
    border: none !important;
    border-radius: var(--sb-radius) !important;
    color: var(--sb-text-secondary) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 10px 18px !important;
    transition: var(--sb-transition) !important;
    white-space: nowrap !important;
    cursor: pointer !important;
}

.tab-nav button:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    color: var(--sb-text-primary) !important;
}

.tab-nav button.selected {
    background: var(--sb-accent-gradient) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
}

.gradio-container:not(.dark) [style*="#e8e8f0"] {
    color: var(--sb-text-primary) !important;
}

.gradio-container:not(.dark) [style*="#a0a0b8"],
.gradio-container:not(.dark) [style*="#8a8a9e"],
.gradio-container:not(.dark) [style*="#6a6a80"],
.gradio-container:not(.dark) [style*="#64748b"] {
    color: var(--sb-text-secondary) !important;
}

.gradio-container:not(.dark) [style*="#1a1a2e"],
.gradio-container:not(.dark) [style*="#12121a"],
.gradio-container:not(.dark) [style*="#0a0a0f"] {
    background: var(--sb-bg-card) !important;
}

/* --- Cards --- */
.stat-card {
    background: var(--sb-bg-card) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius-lg) !important;
    padding: 24px !important;
    transition: var(--sb-transition) !important;
    position: relative;
    overflow: hidden;
}

.stat-card:hover {
    border-color: var(--sb-accent-primary) !important;
    transform: translateY(-2px);
    box-shadow: var(--sb-shadow-lg) !important;
}

.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--sb-accent-gradient);
    opacity: 0;
    transition: var(--sb-transition);
}

.stat-card:hover::before {
    opacity: 1;
}

/* --- Glass Card --- */
.glass-card {
    background: var(--sb-glass) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid var(--sb-glass-border) !important;
    border-radius: var(--sb-radius-lg) !important;
    padding: 24px !important;
    box-shadow: var(--sb-shadow) !important;
}

/* --- Hero Section --- */
.hero-section {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1), rgba(168, 85, 247, 0.08));
    border: 1px solid var(--sb-glass-border);
    border-radius: var(--sb-radius-xl);
    padding: 48px 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.12), transparent 70%);
    border-radius: 50%;
}

.hero-section h2 {
    font-size: 36px !important;
    font-weight: 800 !important;
    background: var(--sb-accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 12px !important;
}

.hero-section p {
    color: var(--sb-text-secondary) !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    max-width: 600px;
}

/* --- Chat Styling --- */
.chatbot, 
.chatbot > div,
.chatbot .message-wrap,
.chatbot .chat-log,
.chatbot .wrapper,
.chatbot .message-row {
    background: var(--sb-bg-secondary) !important;
    border-radius: var(--sb-radius-lg) !important;
}

.chatbot {
    border: 1px solid var(--sb-border) !important;
}

.chatbot .message {
    border-radius: var(--sb-radius) !important;
    padding: 14px 18px !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
    color: var(--sb-text-primary) !important;
}

.chatbot .message p, .chatbot .message span, .chatbot .message div {
    color: var(--sb-text-primary) !important;
}

.chatbot .user {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.15)) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
}

.chatbot .bot {
    background: var(--sb-bg-card) !important;
    border: 1px solid var(--sb-border) !important;
}

/* Fix Plotly wrapper backgrounds and default blocks inside tabs */
.plot-container, .plotly-chart, .gradio-plot, .gradio-plot-container {
    background: var(--sb-bg-card) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius-lg) !important;
}

/* --- Buttons --- */
.primary-btn {
    background: var(--sb-accent-gradient) !important;
    border: none !important;
    border-radius: var(--sb-radius) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0 18px !important;
    min-height: 42px !important;
    min-width: 0 !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    line-height: 1.1 !important;
    white-space: nowrap !important;
    box-sizing: border-box !important;
    transition: var(--sb-transition) !important;
    cursor: pointer !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25) !important;
}

.primary-btn:hover {
    background: var(--sb-accent-gradient-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35) !important;
}

.secondary-btn {
    background: var(--sb-bg-card) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius) !important;
    color: var(--sb-text-primary) !important;
    font-weight: 500 !important;
    padding: 0 16px !important;
    min-height: 40px !important;
    min-width: 0 !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    line-height: 1.1 !important;
    white-space: nowrap !important;
    box-sizing: border-box !important;
    transition: var(--sb-transition) !important;
}

.secondary-btn:hover {
    border-color: var(--sb-accent-primary) !important;
    background: rgba(99, 102, 241, 0.1) !important;
}

/* --- Input Fields --- */
.input-field textarea, .input-field input {
    background: var(--sb-bg-input) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius) !important;
    color: var(--sb-text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    transition: var(--sb-transition) !important;
}

.input-field select,
.input-field button {
    background: var(--sb-bg-input) !important;
    border-color: var(--sb-border) !important;
    color: var(--sb-text-primary) !important;
}

.header-actions {
    display: flex !important;
    align-items: flex-end !important;
    justify-content: flex-end !important;
    gap: 12px !important;
    width: 100% !important;
}

.header-actions > * {
    min-width: 0 !important;
}

.header-model-select {
    width: 100% !important;
    max-width: 360px !important;
}

.header-model-select label {
    font-size: 12px !important;
    color: var(--sb-text-secondary) !important;
}

.header-model-select input,
.header-model-select select,
.header-model-select button {
    min-height: 42px !important;
}

.input-field textarea:focus, .input-field input:focus {
    border-color: var(--sb-accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15) !important;
    outline: none !important;
}

/* --- Accordion --- */
.accordion {
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius) !important;
    background: var(--sb-bg-card) !important;
    margin-top: 8px !important;
}

/* --- Upload Area --- */
.upload-area {
    border: 2px dashed var(--sb-border) !important;
    border-radius: var(--sb-radius-lg) !important;
    background: rgba(99, 102, 241, 0.03) !important;
    transition: var(--sb-transition) !important;
    padding: 40px !important;
}

.upload-area:hover {
    border-color: var(--sb-accent-primary) !important;
    background: rgba(99, 102, 241, 0.06) !important;
}

/* --- Progress Bar --- */
.progress-bar {
    background: var(--sb-bg-input) !important;
    border-radius: 20px !important;
    overflow: hidden !important;
    height: 10px !important;
}

.progress-bar .progress-fill {
    background: var(--sb-accent-gradient) !important;
    border-radius: 20px !important;
    transition: width 0.5s ease !important;
    height: 100% !important;
}

/* --- Flashcard --- */
.flashcard-container {
    perspective: 1000px;
    width: 100%;
    min-height: 250px;
    margin: 20px 0;
}

.flashcard {
    position: relative;
    width: 100%;
    min-height: 250px;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    transform-style: preserve-3d;
}

.flashcard.flipped {
    transform: rotateY(180deg);
}

.flashcard-front, .flashcard-back {
    position: absolute;
    inset: 0;
    backface-visibility: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px;
    border-radius: var(--sb-radius-xl);
    font-size: 18px;
    line-height: 1.6;
    text-align: center;
}

.flashcard-front {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
    border: 1px solid rgba(99, 102, 241, 0.25);
    color: var(--sb-text-primary);
}

.flashcard-back {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.12), rgba(16, 185, 129, 0.08));
    border: 1px solid rgba(34, 197, 94, 0.25);
    color: var(--sb-text-primary);
    transform: rotateY(180deg);
}

/* --- Badge --- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

.badge-success { background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.25); }
.badge-warning { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.25); }
.badge-error { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.25); }
.badge-info { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.25); }
.badge-primary { background: rgba(99, 102, 241, 0.15); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.25); }

/* --- Score Display --- */
.score-display {
    font-size: 48px;
    font-weight: 800;
    background: var(--sb-accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    padding: 20px;
}

/* --- Empty State --- */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: var(--sb-text-muted);
}

.empty-state .icon {
    font-size: 48px;
    margin-bottom: 16px;
    opacity: 0.5;
}

.empty-state h3 {
    color: var(--sb-text-secondary) !important;
    margin-bottom: 8px !important;
    font-weight: 600 !important;
}

.empty-state p {
    font-size: 14px !important;
    line-height: 1.6 !important;
}

/* --- Skeleton Loading --- */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.skeleton {
    background: linear-gradient(90deg, var(--sb-bg-card) 25%, var(--sb-bg-card-hover) 50%, var(--sb-bg-card) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: var(--sb-radius);
}

/* --- Pulse Animation --- */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.3); }
    50% { box-shadow: 0 0 0 8px rgba(99, 102, 241, 0); }
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--sb-accent-primary);
    animation: pulse-glow 2s infinite;
    display: inline-block;
}

/* --- Source Citation --- */
.source-citation {
    background: var(--sb-bg-card);
    border: 1px solid var(--sb-border);
    border-left: 3px solid var(--sb-accent-primary);
    border-radius: 0 var(--sb-radius) var(--sb-radius) 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 13px;
    line-height: 1.6;
}

.source-citation strong {
    color: var(--sb-accent-primary);
}

/* --- Confidence Meter --- */
.confidence-meter {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 12px 0;
}

.confidence-bar-bg {
    flex: 1;
    height: 6px;
    background: var(--sb-bg-input);
    border-radius: 3px;
    overflow: hidden;
}

.confidence-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}

.confidence-high { background: var(--sb-success); }
.confidence-medium { background: var(--sb-warning); }
.confidence-low { background: var(--sb-error); }

/* --- Quiz Question Card --- */
.quiz-question {
    background: var(--sb-bg-card);
    border: 1px solid var(--sb-border);
    border-radius: var(--sb-radius-lg);
    padding: 24px;
    margin: 12px 0;
}

.quiz-question h4 {
    color: var(--sb-accent-primary) !important;
    margin-bottom: 12px !important;
}

/* --- Result Cards --- */
.result-correct {
    border-left: 4px solid var(--sb-success) !important;
    background: rgba(34, 197, 94, 0.05) !important;
}

.result-incorrect {
    border-left: 4px solid var(--sb-error) !important;
    background: rgba(239, 68, 68, 0.05) !important;
}

.result-partial {
    border-left: 4px solid var(--sb-warning) !important;
    background: rgba(245, 158, 11, 0.05) !important;
}

/* --- File List Item --- */
.file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    background: var(--sb-bg-card);
    border: 1px solid var(--sb-border);
    border-radius: var(--sb-radius);
    margin: 6px 0;
    transition: var(--sb-transition);
}

.file-item:hover {
    border-color: var(--sb-accent-primary);
}

/* --- Scrollbar --- */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--sb-border);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--sb-border-light);
}

/* --- Responsive --- */
@media (max-width: 768px) {
    .app-header {
        padding: 16px 20px;
        flex-direction: column;
        align-items: flex-start;
    }

    .app-header h1 {
        font-size: 22px !important;
    }

    .hero-section {
        padding: 32px 24px;
    }

    .hero-section h2 {
        font-size: 24px !important;
    }

    .tab-nav button {
        font-size: 12px !important;
        padding: 8px 14px !important;
    }

    .header-actions {
        width: 100% !important;
        flex-direction: column !important;
        align-items: stretch !important;
    }

    .header-model-select {
        max-width: none !important;
    }

    #theme-toggle-btn {
        width: 100% !important;
        max-width: none !important;
    }
}

/* --- Markdown Content Styling --- */
.markdown-content h1, .markdown-content h2, .markdown-content h3 {
    color: var(--sb-text-primary) !important;
    font-weight: 700 !important;
    margin-top: 20px !important;
}

.markdown-content h1 { font-size: 24px !important; }
.markdown-content h2 { font-size: 20px !important; }
.markdown-content h3 { font-size: 17px !important; }

.markdown-content p {
    line-height: 1.7 !important;
    color: var(--sb-text-secondary) !important;
}

.markdown-content code {
    background: var(--sb-bg-input) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 6px !important;
    padding: 2px 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    color: #c084fc !important;
}

.markdown-content pre {
    background: var(--sb-bg-input) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius) !important;
    padding: 16px !important;
    overflow-x: auto !important;
}

.markdown-content blockquote {
    border-left: 3px solid var(--sb-accent-primary) !important;
    padding-left: 16px !important;
    color: var(--sb-text-secondary) !important;
    font-style: italic !important;
    margin: 12px 0 !important;
}

.markdown-content ul, .markdown-content ol {
    padding-left: 24px !important;
    color: var(--sb-text-secondary) !important;
}

.markdown-content li {
    margin: 4px 0 !important;
    line-height: 1.7 !important;
}

.markdown-content table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 16px 0 !important;
}

.markdown-content th, .markdown-content td {
    border: 1px solid var(--sb-border) !important;
    padding: 10px 14px !important;
    text-align: left !important;
}

.markdown-content th {
    background: var(--sb-bg-card) !important;
    font-weight: 600 !important;
    color: var(--sb-text-primary) !important;
}

.markdown-content hr {
    border: none !important;
    border-top: 1px solid var(--sb-border) !important;
    margin: 24px 0 !important;
}

/* --- Toast Notification --- */
@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOut {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}

/* --- Loading Spinner --- */
@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner {
    width: 24px;
    height: 24px;
    border: 3px solid var(--sb-border);
    border-top-color: var(--sb-accent-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
}

/* --- Plotly Chart Container --- */
.plotly-chart {
    background: var(--sb-bg-card) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: var(--sb-radius-lg) !important;
    padding: 16px !important;
}

/* --- Section Headers --- */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--sb-border);
}

.section-header h3 {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: var(--sb-text-primary) !important;
    margin: 0 !important;
}

/* --- Focus Ring Fix --- */
*:focus-visible {
    outline: 2px solid var(--sb-accent-primary) !important;
    outline-offset: 2px !important;
}

#theme-toggle-btn {
    margin-top: 0 !important;
    height: 42px !important;
    min-width: 42px !important;
    max-width: 42px !important;
    padding: 0 !important;
    font-size: 18px !important;
    border-radius: var(--sb-radius) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
"""
