import sounddevice as sd
import faster_whisper

from ferdi.stt.base import STTProvider


class WhisperSTT(STTProvider):
    """STTProvider that records audio from the microphone and transcribes locally using faster-whisper."""

    def __init__(
        self,
        model: str = "base",
        initial_prompt: str | None = None,
        record_seconds: float = 5.0,
    ) -> None:
        self.model = model
        self.initial_prompt = initial_prompt
        self.record_seconds = record_seconds
        # Lazily initialized on first call to listen() to avoid loading the model at construction time.
        self._whisper_model: faster_whisper.WhisperModel | None = None

    def _get_model(self) -> faster_whisper.WhisperModel:
        if self._whisper_model is None:
            self._whisper_model = faster_whisper.WhisperModel(
                self.model, device="cpu", compute_type="int8"
            )
        return self._whisper_model

    def listen(self) -> str:
        """Record audio for up to record_seconds, transcribe, and return the text."""
        sample_rate = 16000
        num_frames = int(sample_rate * self.record_seconds)

        audio = sd.rec(num_frames, samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()

        # faster-whisper expects a 1-D float32 numpy array
        audio_1d = audio[:, 0] if audio.ndim == 2 else audio

        kwargs: dict = {"language": "en"}
        if self.initial_prompt is not None:
            kwargs["initial_prompt"] = self.initial_prompt

        segments, _info = self._get_model().transcribe(audio_1d, **kwargs)
        return "".join(segment.text for segment in segments).strip()
