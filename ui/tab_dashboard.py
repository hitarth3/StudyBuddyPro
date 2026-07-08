from __future__ import annotations

"""
StudyBuddy Pro — Dashboard Tab

Landing page with hero section, quick stats, learning progress charts,
topic analysis, and getting-started guide.
"""

import gradio as gr
import plotly.graph_objects as go

from memory.persistence import session_memory
from backend.analytics import analytics_engine
from ui.components import stat_card_html, empty_state_html, icon


def create_dashboard_tab() -> None:
    """Build the dashboard tab content."""

    # Hero Section
    gr.HTML("""
    <div class="hero-section">
        <h2>✨ Welcome to StudyBuddy Pro</h2>
        <p>Your AI-powered study assistant that transforms your notes into an intelligent personal tutor.
        Upload your study material, ask questions, generate quizzes, create flashcards, and ace your exams.</p>
    </div>
    """)

    # Quick Stats
    with gr.Row(equal_height=True):
        stats_display = gr.HTML(value=_render_stats(), elem_id="dashboard-stats")

    # Learning Progress Charts & Topic Analysis
    gr.HTML("""
    <div class="section-header" style="margin-top: 24px;">
        <h3>📊 Learning Progress</h3>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-bottom: 8px;">📈 Quiz Scores Over Time</div>')
            scores_chart = gr.Plot(value=_build_scores_chart(), elem_id="scores-chart")

        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-bottom: 8px;">🎯 Topic Accuracy</div>')
            accuracy_chart = gr.Plot(value=_build_accuracy_chart(), elem_id="accuracy-chart")

    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-top: 16px; margin-bottom: 8px;">🧠 Topic Strength Analysis</div>')
            weak_topics_display = gr.HTML(value=_render_weak_topics(), elem_id="weak-topics")
        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-top: 16px; margin-bottom: 8px;">📅 Daily Study Activity</div>')
            activity_display = gr.HTML(value=_render_activity(), elem_id="activity-display")

    # Quick Actions / Guide
    gr.HTML("""
    <div style="margin: 24px 0 12px 0;">
        <h3 style="font-size: 18px; font-weight: 700; color: #e8e8f0; margin-bottom: 16px;">
            🚀 Quick Start Guide
        </h3>
    </div>
    """)

    with gr.Row(equal_height=True):
        gr.HTML("""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.06));
                    border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 16px; padding: 24px;">
            <div style="font-size: 28px; margin-bottom: 12px;">📤</div>
            <h4 style="color: #e8e8f0; font-weight: 700; margin-bottom: 8px;">1. Upload Material</h4>
            <p style="color: #a0a0b8; font-size: 14px; line-height: 1.6;">
                Upload your PDFs, DOCX, or TXT study files. We'll process and index them for AI-powered learning.
            </p>
        </div>
        """)
        gr.HTML("""
        <div style="background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(168, 85, 247, 0.06));
                    border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 16px; padding: 24px;">
            <div style="font-size: 28px; margin-bottom: 12px;">💬</div>
            <h4 style="color: #e8e8f0; font-weight: 700; margin-bottom: 8px;">2. Ask Questions</h4>
            <p style="color: #a0a0b8; font-size: 14px; line-height: 1.6;">
                Chat with your notes. Get answers with citations, explanations at any level, and follow-up discussions.
            </p>
        </div>
        """)
        gr.HTML("""
        <div style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(99, 102, 241, 0.06));
                    border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 16px; padding: 24px;">
            <div style="font-size: 28px; margin-bottom: 12px;">📝</div>
            <h4 style="color: #e8e8f0; font-weight: 700; margin-bottom: 8px;">3. Test Yourself</h4>
            <p style="color: #a0a0b8; font-size: 14px; line-height: 1.6;">
                Generate quizzes, flashcards, and revision notes. Track your progress and identify weak areas.
            </p>
        </div>
        """)

    # Refresh dashboard
    with gr.Row():
        refresh_btn = gr.Button("🔄 Refresh Dashboard & Analytics", elem_classes=["secondary-btn"], size="sm")

    # Wiring dashboard refresh callback
    def _refresh_dashboard():
        return (
            _render_stats(),
            _build_scores_chart(),
            _build_accuracy_chart(),
            _render_weak_topics(),
            _render_activity(),
        )

    refresh_btn.click(
        fn=_refresh_dashboard,
        outputs=[stats_display, scores_chart, accuracy_chart, weak_topics_display, activity_display],
    )


def _render_stats() -> str:
    """Render the stats cards HTML."""
    stats = analytics_engine.get_overall_stats()
    files = session_memory.get_uploaded_files()

    cards = [
        stat_card_html("Documents", str(stats["total_documents"]),
                       f"{sum(f.get('chunks', 0) for f in files)} chunks indexed", "book"),
        stat_card_html("Quizzes Taken", str(stats["total_quizzes"]),
                       f"Avg: {stats['average_score']:.0f}%", "quiz"),
        stat_card_html("Accuracy", f"{stats['overall_accuracy']:.0f}%",
                       f"{stats['total_correct']}/{stats['total_questions']} correct", "target"),
        stat_card_html("Study Streak", f"{stats['study_streak']} days",
                       "Keep it up! 🔥" if stats["study_streak"] > 0 else "Start today!", "fire"),
    ]

    return f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
        {"".join(cards)}
    </div>
    """


def _build_scores_chart() -> go.Figure:
    """Build quiz scores line chart."""
    data = analytics_engine.get_quiz_scores()
    fig = go.Figure()

    if data.get("has_data"):
        fig.add_trace(go.Scatter(
            x=data["labels"],
            y=data["scores"],
            mode="lines+markers",
            name="Score",
            line=dict(color="#6366f1", width=3),
            marker=dict(size=8, color="#8b5cf6"),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.1)",
        ))
    else:
        fig.add_annotation(
            text="No quiz data yet. Take some quizzes to see your progress.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#6a6a80"),
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=20, b=40),
        height=280,
        xaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.2)",
            tickfont=dict(color="#8a8a9e"),
        ),
        yaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.2)",
            tickfont=dict(color="#8a8a9e"),
            range=[0, 105],
        ),
        font=dict(color="#8a8a9e"),
    )

    return fig


def _build_accuracy_chart() -> go.Figure:
    """Build topic accuracy bar chart."""
    data = analytics_engine.get_topic_accuracy()
    fig = go.Figure()

    if data.get("has_data"):
        colors = ["#22c55e" if acc >= 60 else "#ef4444" for acc in data["accuracy"]]
        fig.add_trace(go.Bar(
            x=data["topics"],
            y=data["accuracy"],
            marker_color=colors,
            text=[f"{a:.0f}%" for a in data["accuracy"]],
            textposition="auto",
        ))
    else:
        fig.add_annotation(
            text="No topic data yet. Take quizzes to see topic accuracy.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14, color="#6a6a80"),
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=20, b=40),
        height=280,
        xaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.2)",
            tickfont=dict(color="#8a8a9e"),
        ),
        yaxis=dict(
            gridcolor="rgba(128, 128, 128, 0.15)",
            zerolinecolor="rgba(128, 128, 128, 0.2)",
            tickfont=dict(color="#8a8a9e"),
            range=[0, 105],
        ),
        font=dict(color="#8a8a9e"),
    )

    return fig


def _render_weak_topics() -> str:
    """Render weak/strong topics analysis."""
    data = analytics_engine.get_weak_strong_topics()

    if not data.get("has_data"):
        return empty_state_html(
            "No Topic Data",
            "Take some quizzes to see your weak and strong topics analysis.",
            "brain"
        )

    html = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">'

    # Weak topics
    html += '<div style="background: var(--sb-bg-card); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 16px;">'
    html += '<h4 style="color: #ef4444; margin-bottom: 12px; font-size: 14px; font-weight: bold;">⚠️ Weak Topics</h4>'
    if data["weak"]:
        for t in data["weak"][:4]:
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 6px 0;
                        border-bottom: 1px solid rgba(239, 68, 68, 0.1); font-size: 13px;">
                <span style="color: var(--sb-text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 130px;">{t['topic']}</span>
                <span class="badge badge-error">{t['accuracy']:.0f}%</span>
            </div>
            """
    else:
        html += '<p style="color: var(--sb-text-muted); font-size: 13px;">No weak topics! Great job! 🎉</p>'
    html += '</div>'

    # Strong topics
    html += '<div style="background: var(--sb-bg-card); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 16px; padding: 16px;">'
    html += '<h4 style="color: #22c55e; margin-bottom: 12px; font-size: 14px; font-weight: bold;">✅ Strong Topics</h4>'
    if data["strong"]:
        for t in data["strong"][:4]:
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 6px 0;
                        border-bottom: 1px solid rgba(34, 197, 94, 0.1); font-size: 13px;">
                <span style="color: var(--sb-text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap; max-width: 130px;">{t['topic']}</span>
                <span class="badge badge-success">{t['accuracy']:.0f}%</span>
            </div>
            """
    else:
        html += '<p style="color: var(--sb-text-muted); font-size: 13px;">Take quizzes to identify strong topics.</p>'
    html += '</div>'

    html += '</div>'
    return html


def _render_activity() -> str:
    """Render study activity summary."""
    data = analytics_engine.get_activity_data()

    if not data.get("has_data"):
        return empty_state_html(
            "No Activity Yet",
            "Start studying to track your daily activity.",
            "clock"
        )

    html = '<div style="display: flex; gap: 8px; flex-wrap: wrap;">'
    for date_str, count in zip(data["dates"][-14:], data["counts"][-14:]):  # Last 14 days
        intensity = min(count * 25, 100)
        html += f"""
        <div style="width: 28px; height: 28px; border-radius: 6px;
                    background: rgba(99, 102, 241, {intensity / 100});
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 10px; color: #e8e8f0;"
             title="{date_str}: {count} activities">
            {count}
        </div>
        """
    html += '</div>'

    return html
