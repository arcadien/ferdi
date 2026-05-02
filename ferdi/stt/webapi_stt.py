import queue

from fastapi import FastAPI
from pydantic import BaseModel

from ferdi.stt.base import STTProvider


class _STTRequest(BaseModel):
    text: str


class WebAPISTT(STTProvider):
    """STTProvider that receives transcribed text via HTTP POST /stt."""

    def __init__(self, port: int = 8000) -> None:
        self.port = port
        self._queue: queue.Queue[str] = queue.Queue()
        self.app = FastAPI()
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.post("/stt")
        def post_stt(request: _STTRequest) -> dict:
            text = request.text
            self._queue.put(text)
            return {"status": "ok", "result": text}

    def listen(self) -> str:
        """Block until a POST /stt request is received and return the text."""
        return self._queue.get()
