import time
import uvicorn
import screeninfo
import yaml
import pydirectinput

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ferdi.stt.base import STTProvider
from ferdi.validators import get_validator

app = FastAPI()

_stt_provider: STTProvider | None = None


def set_stt_provider(provider: STTProvider) -> None:
    """Inject an STTProvider instance into the engine."""
    global _stt_provider
    _stt_provider = provider


class CommandRequest(BaseModel):
    command: str


class QuantumRouteRequest(BaseModel):
    destination: str


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


@app.post("/quantum-route")
def quantum_route(request: QuantumRouteRequest):
    if not hasattr(app.state, "resolution") or app.state.resolution is None:
        raise HTTPException(status_code=400, detail="Resolution not detected. Run detect-resolution first.")

    with open("etc/sc-config.yaml", "r") as f:
        config = yaml.safe_load(f)

    resolution = app.state.resolution
    starmap = config["starmap"]

    x = int(resolution["width"] * starmap["search_field_x_pct"])
    y = int(resolution["height"] * starmap["search_field_y_pct"])

    pydirectinput.press(starmap["key_open"])
    time.sleep(1)
    pydirectinput.moveTo(x, y)
    pydirectinput.click()
    pydirectinput.typewrite(request.destination, interval=0.05)
    pydirectinput.press(starmap["key_validate"])

    validator = get_validator(config)
    if not validator.validate(request.destination):
        raise HTTPException(status_code=500, detail=f"Could not confirm quantum route to {request.destination}")

    pydirectinput.press(starmap["key_close"])
    pydirectinput.press(starmap["key_quantum"])

    return {
        "destination": request.destination,
        "status": "ok",
        "message": f"Quantum route to {request.destination} set",
    }
