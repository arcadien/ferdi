# ferdi

Voice agent for Star Citizen. You speak, ferdi reads the screen and clicks for you.

**Pipeline:** VoiceAttack → FastAPI → Claude Vision → pydirectinput

## Requirements

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.11+

## Installation

```bash
uv sync --extra dev
```

## Start

```bash
uv run serve
```

Server runs on `http://localhost:8000`.

## Status

Work in progress.
