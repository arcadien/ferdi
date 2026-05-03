import uvicorn
import screeninfo

from fastapi import FastAPI, HTTPException
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


def serve():
    uvicorn.run("ferdi.main:app", host="0.0.0.0", port=8000)


@app.post("/command")
def post_command(request: CommandRequest):
    return {"status": "ok", "received": request.command}


@app.post("/detect-resolution")
def detect_resolution():
    monitors = screeninfo.get_monitors()
    primary = next((m for m in monitors if m.is_primary), None)
    if primary is None:
        raise HTTPException(status_code=500, detail="No primary monitor found")
    app.state.resolution = {"width": primary.width, "height": primary.height}
    return {
        "width": primary.width,
        "height": primary.height,
        "message": f"Resolution {primary.width} by {primary.height} detected",
    }
