"""Validators module for route validation."""

from ferdi.validators.base import RouteValidator
from ferdi.validators.bypass import BypassValidator
from ferdi.validators.claude_vision import ClaudeVisionValidator


def get_validator(config: dict) -> RouteValidator:
    """Factory function to get a validator instance from config.

    Args:
        config: Configuration dict with validator type at config["validator"]["type"].

    Returns:
        An instance of the appropriate validator.

    Raises:
        ValueError: If validator type is unknown.
    """
    validator_type = config.get("validator", {}).get("type", "bypass")

    if validator_type == "bypass":
        return BypassValidator()
    elif validator_type == "claude-vision":
        return ClaudeVisionValidator()
    else:
        raise ValueError(f"Unknown validator type: {validator_type}")


__all__ = [
    "RouteValidator",
    "BypassValidator",
    "ClaudeVisionValidator",
    "get_validator",
]
