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
        
        Args:
            prompt: The formatted prompt with text to summarize
            
        Returns:
            The generated summary string from the LLM
            
        Raises:
            ConnectionError: If the Ollama service is unreachable
            RuntimeError: If the API returns a non-200 status
            ValueError: If the response format is unexpected
        """
        # Ensure the timeout is high enough for long summaries on local hardware
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 1024,  # Prevents mid-sentence cutoff
                    "num_ctx": 4096,      # Allows the model to 'remember' the whole input
                    "temperature": 0.7    # Balances coherence and variation
                }
            }
            
            try:
                response = await client.post(
                    f"{self.host}/api/generate",
                    json=request_data 
                )
                response.raise_for_status()
                
            except httpx.ConnectError:
                raise ConnectionError(
                    f"Could not connect to Ollama at {self.host}. "
                    "Please ensure the Ollama service is running."
                )
            except httpx.HTTPStatusError as e:
                raise RuntimeError(
                    f"Ollama API returned an error: {e.response.status_code} - {e.response.text}"
                )
            except httpx.TimeoutException:
                raise RuntimeError(
                    f"Ollama took too long to respond. Current timeout is {self.timeout}s."
                )

            data = response.json()
            
            # Extract the actual summary text
            summary_text = data.get("response")
            
            if not summary_text:
                raise ValueError("Ollama returned an empty response or invalid JSON structure.")

            # Logic Check: Verify if it stopped due to length limits
            if data.get("done_reason") == "length":
                print("Warning: Summary reached the max token limit and may be incomplete.")

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
