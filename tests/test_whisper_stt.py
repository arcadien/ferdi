"""
Acceptance tests for TRQ-006 — WhisperSTT implementation (SPEC-006).

These tests are written before the implementation exists and are expected to
fail (RED) until ferdi/stt/whisper_stt.py is created.
"""

import io
import os
import struct
import wave

import pytest


def _make_wav_bytes(duration_seconds: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Generate a minimal silent WAV file in memory for use as a test fixture."""
    num_frames = int(sample_rate * duration_seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit PCM
        wf.setframerate(sample_rate)
        # Write silent frames (all zeros)
        wf.writeframes(struct.pack(f"<{num_frames}h", *([0] * num_frames)))
    return buf.getvalue()


def test_trq006_whisper_stt_implements_provider():
    """WhisperSTT must be a subclass of STTProvider."""
    from ferdi.stt.base import STTProvider  # noqa: PLC0415
    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    assert issubclass(WhisperSTT, STTProvider), (
        "WhisperSTT must be a subclass of STTProvider"
    )


def test_trq006_whisper_stt_model_configurable():
    """WhisperSTT must store the model name passed at construction."""
    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    instance = WhisperSTT(model="tiny")

    assert instance.model == "tiny", (
        "WhisperSTT must expose the configured model name as .model"
    )


def test_trq006_whisper_stt_initial_prompt_configurable():
    """WhisperSTT must store the initial_prompt passed at construction."""
    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    instance = WhisperSTT(initial_prompt="Star Citizen")

    assert instance.initial_prompt == "Star Citizen", (
        "WhisperSTT must expose the configured initial_prompt as .initial_prompt"
    )


def test_trq006_whisper_stt_record_seconds_configurable():
    """WhisperSTT must store the record_seconds value passed at construction."""
    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    instance = WhisperSTT(record_seconds=3.0)

    assert instance.record_seconds == 3.0, (
        "WhisperSTT must expose the configured record_seconds as .record_seconds"
    )


def test_trq006_whisper_stt_end_to_end(monkeypatch, tmp_path):
    """
    WhisperSTT.listen() must return a non-empty string when transcribing audio.

    Microphone capture is mocked: sounddevice.rec() is replaced with a function
    that writes the silent WAV fixture into the expected buffer so no real hardware
    is needed in CI.
    """
    import numpy as np

    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    # Build silent audio frames as a numpy array (1 second @ 16 kHz, mono, float32)
    sample_rate = 16000
    duration = 1.0
    num_samples = int(sample_rate * duration)
    silent_audio = np.zeros((num_samples, 1), dtype=np.float32)

    # Patch sounddevice.rec to return the silent numpy array immediately
    import sounddevice as sd  # noqa: PLC0415

    def fake_rec(num_frames, samplerate, channels, dtype):  # noqa: ANN001
        return silent_audio

    def fake_wait():
        pass

    monkeypatch.setattr(sd, "rec", fake_rec)
    monkeypatch.setattr(sd, "wait", fake_wait)

    # Patch faster_whisper.WhisperModel to avoid downloading a real model
    import faster_whisper  # noqa: PLC0415

    class FakeSegment:
        text = "hello world"

    class FakeInfo:
        language = "en"
        language_probability = 0.99

    class FakeWhisperModel:
        def __init__(self, model_size_or_path, **kwargs):  # noqa: ANN001
            pass

        def transcribe(self, audio, **kwargs):  # noqa: ANN001
            return [FakeSegment()], FakeInfo()

    monkeypatch.setattr(faster_whisper, "WhisperModel", FakeWhisperModel)

    instance = WhisperSTT(model="tiny", record_seconds=duration)
    result = instance.listen()

    assert isinstance(result, str), "WhisperSTT.listen() must return a string"
    assert len(result) > 0, "WhisperSTT.listen() must return a non-empty string"


def test_trq006_factory_selects_whisper_provider_from_env(monkeypatch):
    """build_stt_provider() with STT_PROVIDER=whisper must return a WhisperSTT instance."""
    monkeypatch.setenv("STT_PROVIDER", "whisper")
    monkeypatch.setenv("WHISPER_MODEL", "tiny")

    # Patch faster_whisper.WhisperModel so the factory does not load a real model
    import faster_whisper  # noqa: PLC0415

    class FakeWhisperModel:
        def __init__(self, model_size_or_path, **kwargs):  # noqa: ANN001
            pass

    monkeypatch.setattr(faster_whisper, "WhisperModel", FakeWhisperModel)

    from ferdi.stt.factory import build_stt_provider  # noqa: PLC0415
    from ferdi.stt.whisper_stt import WhisperSTT  # noqa: PLC0415

    provider = build_stt_provider()

    assert isinstance(provider, WhisperSTT), (
        "build_stt_provider() must return a WhisperSTT when STT_PROVIDER=whisper"
    )
