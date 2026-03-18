"""
Ollama service for interacting with the local LLM inference engine.
"""
import os
from typing import Optional
import httpx
from pydantic import BaseModel


class OllamaRequest(BaseModel):
    """Request model for Ollama API."""
    model: str
    prompt: str
    stream: bool = False


class OllamaResponse(BaseModel):
    """Response model for Ollama API."""
    model: str
    response: str
    done: bool


class OllamaService:
    """Service class for communicating with Ollama."""
    
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://ollama:11434") #"http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "summarizer-model")
        self.timeout = 120.0  # 2 minutes timeout for long texts
          
    async def generate_summary(self, prompt: str) -> str:
        """
        Generate a complete summary using the Ollama model.
        """
        from fastapi import HTTPException # Import inside to avoid circular dependencies if any

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 1024,
                    "num_ctx": 4096,
                    "temperature": 0.7
                }
            }
            
            try:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json=request_data 
                )
                response.raise_for_status()
                
            except httpx.ConnectError:
                # Map connection issues to 503
                raise HTTPException(
                    status_code=503,
                    detail=f"Could not connect to Ollama at {self.host}."
                )
            except httpx.TimeoutException:
                # Map timeouts to 503 (This fixes your failing test!)
                raise HTTPException(
                    status_code=503,
                    detail=f"Ollama took too long to respond (>{self.timeout}s)."
                )
            except httpx.HTTPStatusError as e:
                # Keep 500 for actual API logic crashes
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama API returned an error: {e.response.status_code}"
                )

            data = response.json()
            summary_text = data.get("response")
            
            if not summary_text:
                raise HTTPException(status_code=500, detail="Ollama returned empty response.")

            return summary_text.strip()
    
    async def check_health(self) -> bool:
        """
        Check if Ollama service is accessible.
        
        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


# Singleton instance
ollama_service = OllamaService()
