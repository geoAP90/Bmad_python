"""
FastAPI application for AI_Summarizer.
A private, local-first text summarization engine for scientific and narrative analysis. 
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.routers import summarize


# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    print(f"Starting AI Summarizer API...")
    print(f"Ollama Host: {os.getenv('OLLAMA_HOST', 'http://ollama:11434')}") #"http://localhost:11434"
    print(f"Ollama Model: {os.getenv('OLLAMA_MODEL', 'summarizer-model')}")
    yield
    # Shutdown
    print("Shutting down AI Summarizer API...")


# Create FastAPI application
app = FastAPI(
    title="AI Summarizer API",
    description="A private, local-first text summarization engine for scientific and narrative analysis.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarize.router)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "AI Summarizer API",
        "version": "1.0.0",
        "description": "A private, local-first text summarization engine",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
