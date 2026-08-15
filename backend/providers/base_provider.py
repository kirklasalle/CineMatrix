from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ImageGenerationError(Exception):
    """Custom exception that carries the attempt log across fallback chains."""
    def __init__(self, message: str, attempts: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message)
        self.attempts = attempts or []


class BaseProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    async def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> str:
        """Returns the URL or Base64 of the generated image."""
        pass

    @abstractmethod
    async def verify_connection(self) -> bool:
        """Lightweight check to verify API key and connectivity."""
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        """Returns a list of available models for this provider."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
