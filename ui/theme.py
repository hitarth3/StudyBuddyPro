from __future__ import annotations

"""
StudyBuddy Pro — Custom Gradio Theme

Premium dark/light theme with custom colors, typography, and styling.
"""

import gradio as gr
from gradio.themes import Base
from gradio.themes.utils import colors, fonts, sizes


class StudyBuddyTheme(Base):
    """Custom premium theme for StudyBuddy Pro."""

    def __init__(self) -> None:
        super().__init__(
            primary_hue=colors.indigo,
            secondary_hue=colors.purple,
            neutral_hue=colors.slate,
            font=[
                fonts.GoogleFont("Inter"),
                "ui-sans-serif",
                "system-ui",
                "sans-serif",
            ],
            font_mono=[
                fonts.GoogleFont("JetBrains Mono"),
                "ui-monospace",
                "monospace",
            ],
        )
        self.set(
            # Body
            body_background_fill="*neutral_50",
            body_background_fill_dark="*neutral_950",
            body_text_color="*neutral_800",
            body_text_color_dark="*neutral_200",

            # Blocks
            block_background_fill="*neutral_50",
            block_background_fill_dark="*neutral_900",
            block_border_color="*neutral_200",
            block_border_color_dark="*neutral_800",
            block_border_width="1px",
            block_label_text_color="*neutral_600",
            block_label_text_color_dark="*neutral_300",
            block_radius="*radius_lg",
            block_shadow="0 4px 10px -4px rgba(15, 23, 42, 0.12)",
            block_shadow_dark="0 4px 6px -1px rgba(0, 0, 0, 0.3)",
            block_title_text_color="*neutral_900",
            block_title_text_color_dark="*neutral_100",

            # Buttons
            button_primary_background_fill="linear-gradient(135deg, *primary_600, *secondary_600)",
            button_primary_background_fill_dark="linear-gradient(135deg, *primary_600, *secondary_600)",
            button_primary_background_fill_hover="linear-gradient(135deg, *primary_500, *secondary_500)",
            button_primary_background_fill_hover_dark="linear-gradient(135deg, *primary_500, *secondary_500)",
            button_primary_text_color="white",
            button_primary_text_color_dark="white",
            button_primary_border_color="transparent",
            button_primary_border_color_dark="transparent",
            button_secondary_background_fill="*neutral_100",
            button_secondary_background_fill_dark="*neutral_800",
            button_secondary_text_color="*neutral_700",
            button_secondary_text_color_dark="*neutral_200",
            button_primary_shadow="0 2px 4px rgba(0, 0, 0, 0.2)",
            button_secondary_shadow="0 1px 3px rgba(0, 0, 0, 0.1)",

            # Inputs
            input_background_fill="*neutral_50",
            input_background_fill_dark="*neutral_800",
            input_border_color="*neutral_200",
            input_border_color_dark="*neutral_700",
            input_border_color_focus="*primary_500",
            input_border_color_focus_dark="*primary_500",

            # Panels
            panel_background_fill="*neutral_50",
            panel_background_fill_dark="*neutral_900",
            panel_border_color="*neutral_200",
            panel_border_color_dark="*neutral_800",

            # Spacing
            layout_gap="*spacing_lg",
            section_header_text_size="*text_lg",
        )


def get_theme() -> StudyBuddyTheme:
    """Get the StudyBuddy Pro theme instance."""
    return StudyBuddyTheme()
