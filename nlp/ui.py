"""
Pure formatting helpers for the Streamlit frontend.

These functions take plain data and return plain strings / dicts. They make
no Streamlit calls, so they can be imported and unit-tested without a
running app. All UI rendering lives in app.py, which keeps the two
concerns separate.
"""

from __future__ import annotations


def format_probability(probability: float) -> str:
    """Format a model probability as a percentage string, e.g. '87.3%'."""
    return f"{probability:.1%}"


def confidence_band(probability: float) -> str:
    """Return a coarse confidence label for display next to a prediction."""
    if probability >= 0.8:
        return "High confidence"
    if probability >= 0.5:
        return "Moderate confidence"
    if probability >= 0.3:
        return "Low confidence"
    return "Very low confidence"


def progress_line(achieved: int, target: int, width: int = 20) -> str:
    """Render a fixed-width progress bar as Unicode blocks, e.g. '██░░'."""
    if target <= 0:
        return ""
    ratio = min(1.0, achieved / target)
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


def build_disclaimer(track: str) -> str:
    """Return the scope disclaimer appropriate to *track*."""
    if track == "semantic":
        return (
            "Training-only surface-value matcher: unseen slot values may be "
            "missed. No date/time normalisation or real action is executed."
        )
    if track == "intent":
        return (
            "Simulated route only. No calendar, music, weather or other "
            "external action has been executed."
        )
    return (
        "Sentence-level opinion label only. This is not emotion detection, "
        "sarcasm understanding or a diagnosis."
    )
