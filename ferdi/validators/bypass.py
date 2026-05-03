"""Bypass validator that always returns True."""

from ferdi.validators.base import RouteValidator


class BypassValidator(RouteValidator):
    """Validator that always returns True (for testing)."""

    def validate(self, destination: str) -> bool:
        """Always returns True regardless of destination.
        
        Args:
            destination: The destination name (ignored).
            
        Returns:
            Always True.
        """
        return True
