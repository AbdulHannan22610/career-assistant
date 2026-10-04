"""Initialize the small set of state values used by the Streamlit UI."""

from __future__ import annotations

from typing import Any


def initialize_session_state(state: Any) -> None:
    """Set default result and error values without overwriting user state."""
    state.setdefault("analysis_result", None)
    state.setdefault("analysis_report", "")
    state.setdefault("analysis_error", "")
