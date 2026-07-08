from __future__ import annotations

"""
StudyBuddy Pro — Quiz Tab

Interactive quiz generation, taking, and evaluation with results display.
"""

import json
import gradio as gr

from backend.quiz_engine import quiz_engine
from memory.persistence import session_memory
from ui.components import quiz_result_html, empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_quiz_tab() -> None:
    """Build the quiz tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📝 AI Quiz Generator</h3>
    </div>
    """)

    # --- Quiz Generation Panel ---
    with gr.Group():
        gr.HTML('<div style="padding: 4px 0;"><strong style="color: #e8e8f0;">⚙️ Quiz Settings</strong></div>')

        with gr.Row():
            topic_input = gr.Textbox(
                label="Topic",
                placeholder="e.g., Machine Learning, Chapter 3, All Topics",
                value="all topics",
                elem_classes=["input-field"],
                scale=2,
            )
            quiz_difficulty = gr.Dropdown(
                choices=["easy", "medium", "hard"],
                value="medium",
                label="Difficulty",
                scale=1,
            )

        with gr.Row():
            num_mcq = gr.Slider(minimum=1, maximum=10, value=5, step=1, label="MCQ Questions")
            num_short = gr.Slider(minimum=0, maximum=10, value=5, step=1, label="Short Answer Questions")

        generate_btn = gr.Button("🎲 Generate Quiz", elem_classes=["primary-btn"])

    # --- Status ---
    quiz_status = gr.HTML(value="", elem_id="quiz-status")

    # --- Interactive Quiz Panel ---
    quiz_display = gr.HTML(
        value=empty_state_html("No Quiz Generated", "Configure settings above and click Generate Quiz.", "quiz"),
        elem_id="quiz-display",
    )

    # Answer inputs (dynamic)
    gr.HTML('<div id="answers-section"></div>')

    # We'll use a single Textbox for all answers in JSON format
    answers_input = gr.Textbox(
        label="📝 Your Answers (fill in below)",
        placeholder="After generating a quiz, answer fields will appear here.\nFormat: For MCQs enter the letter (A/B/C/D), for short answers write your response.\nEnter answers separated by ||| (three pipes).\nExample: B ||| A ||| C ||| The answer is... ||| Definition of...",
        lines=5,
        elem_classes=["input-field"],
        visible=True,
    )

    submit_btn = gr.Button("✅ Submit Answers", elem_classes=["primary-btn"], visible=True)

    # --- Results Panel ---
    results_display = gr.HTML(value="", elem_id="quiz-results")

    # --- State ---
    quiz_data_state = gr.State(None)

    # --- Callbacks ---
    def _generate_quiz(topic: str, diff: str, n_mcq: int, n_short: int):
        """Generate a new quiz."""
        result = quiz_engine.generate_quiz(
            topic=topic,
            difficulty=diff,
            num_mcq=int(n_mcq),
            num_short=int(n_short),
        )

        if "error" in result:
            return (
                f'<span class="badge badge-error">❌ {result["error"]}</span>',
                empty_state_html("Quiz Generation Failed", result["error"], "error"),
                "",
                "",
                None,
            )

        questions = result.get("questions", [])
        quiz_html = _render_quiz(questions)

        # Build answer hint
        answer_hint = []
        for q in questions:
            qid = q.get("id", "?")
            q_type = q.get("type", "mcq")
            if q_type == "mcq":
                answer_hint.append(f"Q{qid} (MCQ — A/B/C/D)")
            else:
                answer_hint.append(f"Q{qid} (Short Answer)")

        hint_text = " ||| ".join(answer_hint)

        return (
            f'<span class="badge badge-success">✅ Quiz generated — {len(questions)} questions</span>',
            quiz_html,
            hint_text,
            "",
            result,
        )

    def _submit_answers(answers_text: str, quiz_data: dict | None):
        """Evaluate submitted answers."""
        if not quiz_data or "questions" not in quiz_data:
            return '<span class="badge badge-error">❌ No quiz to evaluate. Generate a quiz first.</span>'

        questions = quiz_data["questions"]

        # Parse answers
        raw_answers = [a.strip() for a in answers_text.split("|||")]
        user_answers = {}

        for i, q in enumerate(questions):
            qid = q.get("id", i + 1)
            if i < len(raw_answers):
                user_answers[qid] = raw_answers[i]
            else:
                user_answers[qid] = ""

        # Evaluate
        evaluation = quiz_engine.evaluate_answers(questions, user_answers)

        if "error" in evaluation:
            return f'<span class="badge badge-error">❌ {evaluation["error"]}</span>'

        # Add topic info to results
        for r in evaluation.get("results", []):
            for q in questions:
                if q.get("id") == r.get("question_id"):
                    r["topic"] = q.get("topic", quiz_data.get("topic", "General"))
                    r["question"] = q.get("question", "")
                    break

        # Save to memory
        session_memory.add_quiz_result({
            "topic": quiz_data.get("topic", "General"),
            "difficulty": quiz_data.get("difficulty", "medium"),
            "results": evaluation.get("results", []),
            "total_marks": evaluation.get("total_marks", 0),
            "max_marks": evaluation.get("max_marks", 0),
            "percentage": evaluation.get("percentage", 0),
        })

        return quiz_result_html(evaluation)

    # Wire events
    generate_btn.click(
        fn=_generate_quiz,
        inputs=[topic_input, quiz_difficulty, num_mcq, num_short],
        outputs=[quiz_status, quiz_display, answers_input, results_display, quiz_data_state],
    )

    submit_btn.click(
        fn=_submit_answers,
        inputs=[answers_input, quiz_data_state],
        outputs=[results_display],
    )


def _render_quiz(questions: list[dict]) -> str:
    """Render quiz questions as HTML."""
    if not questions:
        return empty_state_html("No Questions", "Failed to generate questions.", "error")

    html_parts = []

    for q in questions:
        qid = q.get("id", "?")
        q_type = q.get("type", "mcq")
        question = q.get("question", "")
        difficulty = q.get("difficulty", "?")
        topic = q.get("topic", "?")

        type_badge = "MCQ" if q_type == "mcq" else "Short Answer"
        type_color = "badge-info" if q_type == "mcq" else "badge-primary"

        html = f"""
        <div class="quiz-question">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: 700; color: #e8e8f0;">Question {qid}</span>
                <div style="display: flex; gap: 6px;">
                    <span class="badge {type_color}">{type_badge}</span>
                    <span class="badge badge-warning">{difficulty}</span>
                </div>
            </div>
            <p style="color: #e8e8f0; font-size: 15px; line-height: 1.6; margin-bottom: 12px;">{question}</p>
        """

        if q_type == "mcq" and q.get("options"):
            html += '<div style="display: flex; flex-direction: column; gap: 8px;">'
            for opt in q["options"]:
                html += f"""
                <div style="background: #16162a; border: 1px solid #2a2a45; border-radius: 8px;
                            padding: 10px 14px; color: #a0a0b8; font-size: 14px; cursor: pointer;
                            transition: all 0.2s ease;">{opt}</div>
                """
            html += '</div>'

        html += f'<div style="margin-top: 8px; color: #6a6a80; font-size: 12px;">📌 Topic: {topic}</div>'
        html += '</div>'
        html_parts.append(html)

    return "\n".join(html_parts)
