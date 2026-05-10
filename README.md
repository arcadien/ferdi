# ferdi

Agent vocal pour Star Citizen. Tu parles, ferdi voit l'écran et clique à ta place.

**Pipeline :** VoiceAttack → FastAPI → Claude Vision → pydirectinput

## Prérequis

- [uv](https://docs.astral.sh/uv/) installé
- Python 3.11+

## Installation

```bash
uv sync --extra dev
```

## Démarrage

```bash
uv run serve
```

Le serveur démarre sur `http://localhost:8000`.

## Status

Work in progress.
