"""
Shared utility helpers.

Small functions used across modules. Each function is independently
importable and has no side effects.
"""

from __future__ import annotations

import re
import unicodedata


def normalise_text(text: str) -> str:
    """Apply NFC normalisation and collapse internal whitespace.

    Mirrors the normalisation used in validate.py so that the app and
    the validator treat identical strings consistently.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text).strip())


def format_probability(probability: float) -> str:
    """Format a model probability as a percentage string, e.g. '87.3%'."""
    return f"{probability:.1%}"


def bar_chart_str(value: float, width: int = 20) -> str:
    """Return a simple Unicode block bar for console/text display."""
    filled = round(value * width)
    return "█" * filled + "░" * (width - filled)
