from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import json
from utils.settings import settings

class AIResponse:
    """Represents a response from the AI service."""
    def __init__(self, text: str, metadata: Optional[Dict] = None):
        self.text = text
        self.metadata = metadata or {}

class AIService(ABC):
    """Abstract base class for AI service implementations."""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the AI service with current settings."""
        pass
    
    @abstractmethod
    async def generate_response(self, message: str, context: List[Dict] = None) -> AIResponse:
        """Generate a response to the given message."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the service is available and properly configured."""
        pass

class AIServiceFactory:
    """Factory for creating AI service instances."""
    
    @staticmethod
    def create_service():
        """Create an AI service instance based on current settings."""
        backend = settings.get("ai_backend", "active_backend")
        
        if backend == "huggingface":
            from .huggingface_backend import HuggingFaceService
            return HuggingFaceService()
        elif backend == "lmstudio":
            from .lmstudio_backend import LMStudioService
            return LMStudioService()
        else:
            raise ValueError(f"Unknown AI backend: {backend}")

class AIServiceManager:
    """Manages AI service lifecycle and configuration."""
    
    def __init__(self):
        self._service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize or reinitialize the AI service."""
        self._service = AIServiceFactory.create_service()
        if not self._service.initialize():
            raise RuntimeError("Failed to initialize AI service")
    
    async def generate_response(self, message: str, context: List[Dict] = None) -> AIResponse:
        """Generate a response using the current AI service."""
        if not self._service or not self._service.is_available():
            self._initialize_service()
        
        try:
            return await self._service.generate_response(message, context)
        except Exception as e:
            # Log the error and return an error response
            error_msg = f"Error generating response: {str(e)}"
            return AIResponse(
                text="I apologize, but I encountered an error while processing your request. "
                     "Please check your settings and try again.",
                metadata={"error": error_msg}
            )
    
    def switch_backend(self):
        """Switch to a different AI backend."""
        self._initialize_service()

# Create global service manager instance
service_manager = AIServiceManager()
