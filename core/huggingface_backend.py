import json
import aiohttp
from typing import Dict, List, Optional
from .ai_service import AIService, AIResponse
from utils.settings import settings

class HuggingFaceService(AIService):
    """HuggingFace API implementation of the AI service."""
    
    def __init__(self):
        self.api_key = None
        self.model = None
        self.endpoint = None
        self.session = None
    
    def initialize(self) -> bool:
        """Initialize the service with current settings."""
        config = settings.get("ai_backend", "huggingface")
        self.api_key = config["api_key"]
        self.model = config["model"]
        self.endpoint = config["endpoint"]
        
        # Create aiohttp session
        if self.session:
            self.session.close()
        self.session = aiohttp.ClientSession(headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        return bool(self.api_key and self.model and self.endpoint)
    
    async def generate_response(self, message: str, context: List[Dict] = None) -> AIResponse:
        """Generate a response using the HuggingFace API."""
        if not self.is_available():
            raise RuntimeError("HuggingFace service is not properly configured")
        
        # Prepare the conversation history
        conversation = []
        if context:
            for msg in context:
                conversation.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the current message
        conversation.append({
            "role": "user",
            "content": message
        })
        
        # Prepare the API request
        api_url = f"{self.endpoint.rstrip('/')}/{self.model}"
        payload = {
            "inputs": self._format_conversation(conversation),
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            async with self.session.post(api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"API request failed: {error_text}")
                
                result = await response.json()
                
                # Extract the generated text from the response
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                else:
                    generated_text = "I apologize, but I couldn't generate a proper response."
                
                return AIResponse(
                    text=generated_text,
                    metadata={
                        "model": self.model,
                        "backend": "huggingface"
                    }
                )
                
        except Exception as e:
            raise RuntimeError(f"Error calling HuggingFace API: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the service is available and properly configured."""
        return bool(self.api_key and self.model and self.endpoint and self.session)
    
    def _format_conversation(self, messages: List[Dict]) -> str:
        """Format the conversation history for the model."""
        formatted = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                formatted += f"Human: {content}\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n"
            elif role == "system":
                formatted += f"System: {content}\n"
        
        formatted += "Assistant:"
        return formatted
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
