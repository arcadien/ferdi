from fastapi import FastAPI
from pydantic import BaseModel

from ferdi.stt.base import STTProvider

app = FastAPI()

_stt_provider: STTProvider | None = None


def set_stt_provider(provider: STTProvider) -> None:
    """Inject an STTProvider instance into the engine."""
    global _stt_provider
    _stt_provider = provider


class CommandRequest(BaseModel):
    command: str


@app.post("/command")
def post_command(request: CommandRequest):
    return {"status": "ok", "received": request.command}
