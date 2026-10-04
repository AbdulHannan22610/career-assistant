"""Load secrets and settings from Streamlit Cloud or a local .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings without exposing secret values to the UI."""

    groq_api_key: str | None
    groq_model: str
    embedding_model: str

    @property
    def has_api_key(self) -> bool:
        """Return whether an API key is configured without returning its value."""
        return bool(self.groq_api_key)


def _streamlit_secret(name: str) -> str | None:
    """Read one Streamlit secret when available, including Cloud deployments."""
    try:
        import streamlit as st

        value = st.secrets.get(name)
    except Exception:
        return None
    return str(value).strip() if value else None



def get_settings() -> Settings:
    """Prefer Streamlit Secrets, then fall back to local environment variables."""
    api_key = _streamlit_secret("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    model = _streamlit_secret("GROQ_MODEL") or os.getenv(
        "GROQ_MODEL", "openai/gpt-oss-120b"
    )
    embedding_model = _streamlit_secret("EMBEDDING_MODEL") or os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    return Settings(
        groq_api_key=api_key,
        groq_model=model,
        embedding_model=embedding_model,
    )
