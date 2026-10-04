"""Create the shared CrewAI-compatible Groq LLM configuration."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any, Iterator

from crewai import LLM

from config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class GroqCrewLLM(LLM):
    """Remove CrewAI's internal cache marker before LiteLLM sends Groq messages."""

    def _format_messages_for_provider(
        self, messages: list[Any]
    ) -> list[dict[str, Any]]:
        formatted_messages = super()._format_messages_for_provider(messages)
        return [
            {key: value for key, value in message.items() if key != "cache_breakpoint"}
            for message in formatted_messages
        ]


def _exception_chain(error: BaseException) -> Iterator[BaseException]:
    """Walk wrapped provider exceptions without looping through cycles."""
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = current.__cause__ or current.__context__


def _provider_error_details(error: BaseException) -> tuple[int | None, str | None]:
    """Read HTTP status and Retry-After from common SDK response objects."""
    status_code = None
    retry_after = None
    for current in _exception_chain(error):
        response = getattr(current, "response", None)
        candidate_status = getattr(current, "status_code", None)
        if candidate_status is None and response is not None:
            candidate_status = getattr(response, "status_code", None)
        if status_code is None and isinstance(candidate_status, int):
            status_code = candidate_status

        headers = getattr(current, "headers", None)
        if headers is None and response is not None:
            headers = getattr(response, "headers", None)
        if retry_after is None and isinstance(headers, Mapping):
            value = headers.get("retry-after") or headers.get("Retry-After")
            if value is not None:
                retry_after = str(value).strip()
    return status_code, retry_after


def _redact_error_message(
    error: BaseException,
    api_key: str | None = None,
    private_text: str | None = None,
) -> str:
    """Keep useful provider detail while removing credentials and resume text."""
    message = str(error)
    if api_key:
        message = message.replace(api_key, "[REDACTED_API_KEY]")
    if private_text:
        message = message.replace(private_text, "[RESUME_TEXT_REDACTED]")
    message = re.sub(r"\bgsk_[A-Za-z0-9_-]+\b", "[REDACTED_GROQ_KEY]", message)
    message = re.sub(
        r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)[^\s,}\"']+",
        r"\1[REDACTED]",
        message,
    )
    message = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer [REDACTED]", message)
    return message[:1200]


def create_llm(settings: Settings | None = None) -> LLM:
    """Build one shared LiteLLM-backed Groq client for the four agents."""
    active_settings = settings or get_settings()
    if not active_settings.groq_api_key:
        raise ValueError(
            "Groq API key is not configured. Add GROQ_API_KEY to your .env "
            "file or Streamlit Secrets."
        )
    return GroqCrewLLM(
        model=f"groq/{active_settings.groq_model}",
        api_key=active_settings.groq_api_key,
        temperature=0.2,
        max_tokens=2048,
    )


def explain_llm_error(
    error: Exception,
    api_key: str | None = None,
    private_text: str | None = None,
) -> str:
    """Log sanitized provider diagnostics and return a useful UI message."""
    status_code, retry_after = _provider_error_details(error)
    safe_message = _redact_error_message(error, api_key, private_text)
    logger.error(
        "CareerAssist AI request failed: exception=%s HTTP_status=%s "
        "Retry-After=%s detail=%s",
        type(error).__name__,
        status_code if status_code is not None else "unavailable",
        retry_after or "unavailable",
        safe_message or "No provider detail supplied",
    )

    message = safe_message.lower()
    if status_code in (401, 403) or any(
        term in message for term in ("authentication", "invalid api key", "unauthorized")
    ):
        return "Groq rejected the API key or account access. Check the key and model permissions in Groq Console."
    if status_code == 429 and any(
        term in message for term in ("tokens per day", "token per day", "daily", "quota", "tpd")
    ):
        return "Groq reports that an account usage quota is exhausted. Check the Groq Console Limits page for the quota and reset time before trying again."
    if status_code == 429 or "rate limit" in message or "too many requests" in message:
        wait = f" Groq requested a wait of {retry_after} seconds." if retry_after else ""
        return (
            "Groq's request rate limit was reached. CrewAI limits retries to at most three "
            f"attempts for an individual request; wait before submitting again.{wait}"
        )
    if status_code == 404 or (
        "model" in message and any(term in message for term in ("not found", "unknown", "unsupported"))
    ):
        return "Groq could not find or serve the configured model. Confirm the model ID and access in Groq Console."
    if any(term in message for term in ("context length", "context window", "too many tokens", "maximum context")):
        return "The request exceeded the model's input limit. Use a shorter, text-based resume and try again."
    if status_code in (400, 422):
        return "Groq rejected an AI request parameter. The sanitized provider detail and HTTP status were logged in the VS Code terminal."
    if status_code is not None and status_code >= 500:
        return "Groq returned a server error. Wait briefly and try the analysis again."
    if any(term in message for term in ("timeout", "connection", "network")):
        return "CareerAssist could not connect to Groq. Check your internet connection and retry."
    return "The AI analysis failed. A sanitized exception and HTTP status (when available) were logged in the VS Code terminal."
