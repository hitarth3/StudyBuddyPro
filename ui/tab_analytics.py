from __future__ import annotations

"""
StudyBuddy Pro — Analytics Tab

Performance dashboard with charts for quiz scores, topic accuracy, and progress.
"""

import gradio as gr
import plotly.graph_objects as go

from backend.analytics import analytics_engine
from backend.quiz_engine import quiz_engine
from memory.persistence import session_memory
from ui.components import stat_card_html, empty_state_html
from utils.logger import get_logger

log = get_logger(__name__)


def create_analytics_tab() -> None:
    """Build the analytics dashboard tab content."""

    gr.HTML("""
    <div class="section-header">
        <h3>📊 Learning Analytics</h3>
    </div>
    """)

    # Overview stats
    stats_display = gr.HTML(value=_render_overview(), elem_id="analytics-stats")

    # Charts
    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-bottom: 8px;">📈 Quiz Scores Over Time</div>')
            scores_chart = gr.Plot(value=_build_scores_chart(), elem_id="scores-chart")

        with gr.Column(scale=1):
            gr.HTML('<div style="color: #e8e8f0; font-weight: 600; margin-bottom: 8px;">🎯 Topic Accuracy</div>')
            accuracy_chart = gr.Plot(value=_build_accuracy_chart(), elem_id="accuracy-chart")

    # Weak topics analysis
    gr.HTML("""
    <div class="section-header" style="margin-top: 24px;">
        <h3>🧠 Topic Analysis</h3>
    </div>
    """)
    weak_topics_display = gr.HTML(value=_render_weak_topics(), elem_id="weak-topics")

    # Activity
    gr.HTML("""
    <div class="section-header" style="margin-top: 24px;">
        <h3>📅 Study Activity</h3>
    </div>
    """)
    activity_display = gr.HTML(value=_render_activity(), elem_id="activity-display")

    # Refresh
    refresh_btn = gr.Button("🔄 Refresh Analytics", elem_classes=["secondary-btn"], size="sm")

    refresh_btn.click(
        fn=_refresh_all,
        outputs=[stats_display, scores_chart, accuracy_chart, weak_topics_display, activity_display],
    )


def _render_overview() -> str:
    """Render overview stats."""
    stats = analytics_engine.get_overall_stats()

    cards = [
        stat_card_html("Total Quizzes", str(stats["total_quizzes"]), "", "quiz"),
        stat_card_html("Overall Accuracy", f'{stats["overall_accuracy"]:.0f}%', "", "target"),
        stat_card_html("Average Score", f'{stats["average_score"]:.0f}%', "", "chart"),
        stat_card_html("Study Streak", f'{stats["study_streak"]} days', "", "fire"),
    ]

    return f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 24px;">
        {"".join(cards)}
    </div>
    """


def _build_scores_chart():
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
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,26,46,0.5)",
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        xaxis=dict(gridcolor="rgba(42,42,69,0.5)", title="Quiz"),
        yaxis=dict(gridcolor="rgba(42,42,69,0.5)", title="Score (%)", range=[0, 105]),
        font=dict(color="#a0a0b8"),
    )

    return fig


def _build_accuracy_chart():
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
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,26,46,0.5)",
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        xaxis=dict(gridcolor="rgba(42,42,69,0.5)"),
        yaxis=dict(gridcolor="rgba(42,42,69,0.5)", title="Accuracy (%)", range=[0, 105]),
        font=dict(color="#a0a0b8"),
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
    html += '<div style="background: #1a1a2e; border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 20px;">'
    html += '<h4 style="color: #ef4444; margin-bottom: 12px;">⚠️ Weak Topics</h4>'
    if data["weak"]:
        for t in data["weak"]:
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0;
                        border-bottom: 1px solid rgba(239, 68, 68, 0.1);">
                <span style="color: #e8e8f0;">{t['topic']}</span>
                <span class="badge badge-error">{t['accuracy']:.0f}%</span>
            </div>
            """
    else:
        html += '<p style="color: #6a6a80; font-size: 14px;">No weak topics! Great job! 🎉</p>'
    html += '</div>'

    # Strong topics
    html += '<div style="background: #1a1a2e; border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 16px; padding: 20px;">'
    html += '<h4 style="color: #22c55e; margin-bottom: 12px;">✅ Strong Topics</h4>'
    if data["strong"]:
        for t in data["strong"]:
            html += f"""
            <div style="display: flex; justify-content: space-between; padding: 8px 0;
                        border-bottom: 1px solid rgba(34, 197, 94, 0.1);">
                <span style="color: #e8e8f0;">{t['topic']}</span>
                <span class="badge badge-success">{t['accuracy']:.0f}%</span>
            </div>
            """
    else:
        html += '<p style="color: #6a6a80; font-size: 14px;">Take quizzes to identify strong topics.</p>'
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
    for date_str, count in zip(data["dates"], data["counts"]):
        intensity = min(count * 25, 100)
        html += f"""
        <div style="width: 32px; height: 32px; border-radius: 6px;
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


def _refresh_all():
    """Refresh all analytics displays."""
    return (
        _render_overview(),
        _build_scores_chart(),
        _build_accuracy_chart(),
        _render_weak_topics(),
        _render_activity(),
    )
