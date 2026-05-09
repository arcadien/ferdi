"""Base abstract class for route validators."""

from abc import ABC, abstractmethod


class RouteValidator(ABC):
    """Abstract base class for quantum route validators."""

    @abstractmethod
    def validate(self, destination: str) -> bool:
        """Validate the quantum route was set correctly.

        Args:
            destination: The destination name.

        Returns:
            True if validation succeeds, False otherwise.
        """
        pass
