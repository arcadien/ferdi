from ferdi.stt.base import STTProvider


class StaticSTT(STTProvider):
    def __init__(self, text: str) -> None:
        self._text = text

    def listen(self) -> str:
        return self._text
