"""Small formatting helpers for report output and score labels."""

from __future__ import annotations

from typing import Any


def format_percentage(value: Any) -> str:
    """Format a fractional score as a percent or show it as unavailable."""
    if value is None:
        return "Unavailable"
    try:
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return "Unavailable"


def display_text(value: Any) -> str:
    """Convert missing values to a clear, consistent display label."""
    if value is None or str(value).strip() == "":
        return "Not found in the resume."
    return str(value).strip()
