import os

from ferdi.stt.base import STTProvider


def build_stt_provider() -> STTProvider:
    """Read STT_PROVIDER from the environment and return the appropriate provider instance."""
    provider_name = os.environ.get("STT_PROVIDER", "").lower()

    if provider_name == "static":
        from ferdi.stt.static_stt import StaticSTT  # noqa: PLC0415

        text = os.environ.get("STT_STATIC_TEXT", "")
        return StaticSTT(text)

    if provider_name == "whisper":
        from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

        model = os.environ.get("WHISPER_MODEL", "base")
        initial_prompt = os.environ.get("WHISPER_INITIAL_PROMPT") or None
        record_seconds = float(os.environ.get("WHISPER_RECORD_SECONDS", "5.0"))
        return WhisperSTT(model=model, initial_prompt=initial_prompt, record_seconds=record_seconds)

    if provider_name == "webapi":
        from ferdi.stt.webapi_stt import WebAPISTT  # noqa: PLC0415

        port = int(os.environ.get("WEBAPI_STT_PORT", "8000"))
        return WebAPISTT(port=port)

    raise ValueError(
        f"Unknown STT_PROVIDER value: {provider_name!r}. "
        "Supported values: 'static', 'whisper', 'webapi'."
    )
