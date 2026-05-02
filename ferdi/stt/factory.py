import os

from ferdi.stt.base import STTProvider


def build_stt_provider() -> STTProvider:
    """Read STT_PROVIDER from the environment and return the appropriate provider instance."""
    provider_name = os.environ.get("STT_PROVIDER", "").lower()

    if provider_name == "static":
        from ferdi.stt.static_stt import StaticSTT  # noqa: PLC0415

        text = os.environ.get("STT_STATIC_TEXT", "")
        return StaticSTT(text)

    raise ValueError(
        f"Unknown STT_PROVIDER value: {provider_name!r}. "
        "Supported values: 'static'."
    )
