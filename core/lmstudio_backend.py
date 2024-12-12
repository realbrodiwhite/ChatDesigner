import json
import aiohttp
from typing import Dict, List, Optional
from .ai_service import AIService, AIResponse
from utils.settings import settings

class LMStudioService(AIService):
    """LM Studio local API implementation of the AI service."""
    
    def __init__(self):
        self.host = None
        self.port = None
        self.model_path = None
        self.session = None
        self.api_base = None
    
    def initialize(self) -> bool:
        """Initialize the service with current settings."""
        config = settings.get("ai_backend", "lmstudio")
        self.host = config["host"]
        self.port = config["port"]
        self.model_path = config["model_path"]
        self.api_base = f"http://{self.host}:{self.port}/v1"
        
        # Create aiohttp session
        if self.session:
            self.session.close()
        self.session = aiohttp.ClientSession(headers={
            "Content-Type": "application/json"
        })
        
        return bool(self.host and self.port)
    
    async def generate_response(self, message: str, context: List[Dict] = None) -> AIResponse:
        """Generate a response using the LM Studio local API."""
        if not self.is_available():
            raise RuntimeError("LM Studio service is not properly configured")
        
        # Prepare the conversation history
        messages = []
        if context:
            messages.extend([{
                "role": msg["role"],
                "content": msg["content"]
            } for msg in context])
        
        # Add the current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        # Prepare the API request
        api_url = f"{self.api_base}/chat/completions"
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
            "stream": False
        }
        
        try:
            async with self.session.post(api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"API request failed: {error_text}")
                
                result = await response.json()
                
                # Extract the generated text from the response
                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"]
                else:
                    generated_text = "I apologize, but I couldn't generate a proper response."
                
                return AIResponse(
                    text=generated_text,
                    metadata={
                        "model": "local",
                        "backend": "lmstudio"
                    }
                )
                
        except Exception as e:
            raise RuntimeError(f"Error calling LM Studio API: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the service is available and properly configured."""
        return bool(self.host and self.port and self.session)
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None
