from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CommandRequest(BaseModel):
    command: str


@app.post("/command")
def post_command(request: CommandRequest):
    return {"status": "ok", "received": request.command}
