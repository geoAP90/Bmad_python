"""
Summarize router for the FastAPI application.
Contains the /summarize endpoint for text summarization.
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.services.ollama_service import ollama_service
from app.prompts.templates import get_simple_researcher_prompt


# Request model
class SummarizeRequest(BaseModel):
    """Request model for the /summarize endpoint."""
    text: str = Field(..., min_length=10, description="The text to be summarized")
    domain: str = Field(default="general research", description="The subject domain for context")


# Response model
class SummarizeResponse(BaseModel):
    """Response model for the /summarize endpoint."""
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float


# Router instance
router = APIRouter(prefix="/summarize", tags=["summarization"])


@router.post("", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize the given text using the researcher persona.
    
    This endpoint uses a persona-driven prompt to ensure 
    summaries are objective, concise, and research-focused.
    
    Args:
        request: The summarize request containing text and optional domain
        
    Returns:
        SummarizeResponse with the summary and metadata
        
    Raises:
        HTTPException: If summarization fails
    """
    try:
        # Generate researcher persona prompt
        prompt = get_simple_researcher_prompt(request.text)
        
        # Get summary from Ollama
        summary = await ollama_service.generate_summary(prompt)
        
        # Calculate compression metrics
        original_length = len(request.text)
        summary_length = len(summary)
        compression_ratio = (1 - summary_length / original_length) * 100 if original_length > 0 else 0
        
        return SummarizeResponse(
            summary=summary,
            original_length=original_length,
            summary_length=summary_length,
            compression_ratio=round(compression_ratio, 2)
        )
        
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ollama service unavailable: {str(e)}"
        )
    except RuntimeError as e:
        # Check if the error message mentions a timeout
        if "timeout" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Ollama service timed out: {str(e)}"
            )
        # Otherwise, keep it as a 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/health")
async def check_ollama_health():
    """
    Check if the Ollama service is accessible.
    
    Returns:
        Health status of the Ollama service
    """
    is_healthy = await ollama_service.check_health()
    
    if is_healthy:
        return {"status": "healthy", "service": "ollama"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama service is not accessible"
        )
