from abc import ABC, abstractmethod


class STTProvider(ABC):
    @abstractmethod
    def listen(self) -> str:
        """Block until a voice command is available and return it as text."""
        ...
