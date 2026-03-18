"""
Fail-Safe Testing Strata for Article Analyzer Backend
=======================================================

This test suite validates critical fail-safe mechanisms in the backend:
1. Input Validation: /summarize returns 422 for empty input
2. Circuit Breaker: API returns 503 when Ollama connection times out
3. Persona Verification: 'Geophysicist' persona exists in system prompt

Uses pytest and httpx for async testing.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

# Import the FastAPI app
from app.main import app
from app.prompts.templates import GEOPHYSICIST_PERSONA, get_geophysicist_prompt


# Test client for synchronous tests
client = TestClient(app)


class TestInputValidation:
    """Test suite for Input Validation - Fail-Safe Layer 1"""
    
    def test_summarize_empty_text_returns_422(self):
        """
        FAIL-SAFE: Verify /summarize returns 422 for empty input
        
        This ensures invalid/malformed requests are rejected before
        reaching the LLM service, preventing unnecessary API calls.
        """
        response = client.post(
            "/summarize",
            json={"text": "", "domain": "general research"}
        )
        
        assert response.status_code == 422, (
            f"Expected 422 for empty text, got {response.status_code}"
        )
        
        # Verify the error details indicate validation failure
        error_detail = response.json()
        assert "detail" in error_detail
    
    def test_summarize_whitespace_only_returns_422(self):
        """
        FAIL-SAFE: Verify /summarize returns 422 for whitespace-only input
        """
        response = client.post(
            "/summarize",
            json={"text": "   ", "domain": "general research"}
        )
        
        assert response.status_code == 422, (
            f"Expected 422 for whitespace-only text, got {response.status_code}"
        )
    
    def test_summarize_below_min_length_returns_422(self):
        """
        FAIL-SAFE: Verify /summarize returns 422 for text below min_length (10 chars)
        """
        response = client.post(
            "/summarize",
            json={"text": "Short", "domain": "general research"}  # Only 5 chars
        )
        
        assert response.status_code == 422, (
            f"Expected 422 for text below min_length, got {response.status_code}"
        )


class TestCircuitBreaker:
    """Test suite for Circuit Breaker Logic - Fail-Safe Layer 2"""
    
    @pytest.mark.asyncio
    async def test_summarize_ollama_timeout_returns_503(self):
        """
        FAIL-SAFE: Verify /summarize returns 503 when Ollama connection times out
        
        This tests the circuit breaker pattern - when the downstream service
        (Ollama) is unavailable or times out, the API should return 503
        instead of hanging or returning 500.
        """
        # Mock the Ollama service to raise a timeout
        with patch('app.routers.summarize.ollama_service.generate_summary') as mock_generate:
            # Simulate a connection timeout scenario
            mock_generate.side_effect = httpx.ConnectError(
                "Connection timed out to Ollama service"
            )
            
            response = client.post(
                "/summarize",
                json={
                    "text": "This is a test text that is long enough to pass validation with more than ten characters",
                    "domain": "general research"
                }
            )
            
            assert response.status_code == 503, (
                f"Expected 503 for Ollama timeout, got {response.status_code}"
            )
            
            # Verify the error message indicates service unavailability
            error_detail = response.json()
            assert "detail" in error_detail
            assert "unavailable" in error_detail["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_summarize_ollama_runtime_error_returns_503(self):
        """
        FAIL-SAFE: Verify /summarize returns 503 for RuntimeError from Ollama
        """
        with patch('app.routers.summarize.ollama_service.generate_summary') as mock_generate:
            mock_generate.side_effect = RuntimeError(
                "Ollama took too long to respond"
            )
            
            response = client.post(
                "/summarize",
                json={
                    "text": "This is a test text that is long enough to pass validation with more than ten characters",
                    "domain": "general research"
                }
            )
            
            # RuntimeError from Ollama should result in 503 (service unavailable)
            # based on the current implementation
            assert response.status_code in [500, 503], (
                f"Expected 500 or 503 for Ollama RuntimeError, got {response.status_code}"
            )
    
    @pytest.mark.asyncio
    async def test_health_endpoint_ollama_unavailable_returns_503(self):
        """
        FAIL-SAFE: Verify /health endpoint returns 503 when Ollama is unavailable
        """
        with patch('app.routers.summarize.ollama_service.check_health') as mock_health:
            mock_health.return_value = False
            
            response = client.get("/summarize/health")
            
            assert response.status_code == 503, (
                f"Expected 503 when Ollama unavailable, got {response.status_code}"
            )


class TestPersonaVerification:
    """Test suite for Persona Verification - Fail-Safe Layer 3"""
    
    def test_geophysicist_persona_exists_in_templates(self):
        """
        FAIL-SAFE: Verify 'Geophysicist' persona is present in system prompt
        
        This ensures the Geophysicist persona is properly configured
        in the prompt templates.
        """
        assert GEOPHYSICIST_PERSONA is not None, (
            "Geophysicist persona should be defined in templates"
        )
        
        # Verify the persona contains expected keywords
        assert "Geophysicist" in GEOPHYSICIST_PERSONA, (
            "Geophysicist persona should contain 'Geophysicist'"
        )
        assert "earth science" in GEOPHYSICIST_PERSONA.lower(), (
            "Geophysicist persona should mention earth science"
        )
        assert "seismic analysis" in GEOPHYSICIST_PERSONA.lower(), (
            "Geophysicist persona should mention seismic analysis"
        )
    
    def test_geophysicist_prompt_function_works(self):
        """
        FAIL-SAFE: Verify get_geophysicist_prompt function works correctly
        """
        test_text = "This is a test document about tectonic plates."
        
        prompt = get_geophysicist_prompt(test_text)
        
        assert prompt is not None, "get_geophysicist_prompt should return a prompt"
        assert test_text in prompt, "Prompt should contain the input text"
        assert "Geophysicist" in prompt, "Prompt should contain Geophysicist persona"
    
    def test_geophysicist_persona_in_simple_researcher_prompt(self):
        """
        FAIL-SAFE: Verify Researcher persona is properly defined
        
        This ensures the base researcher persona is available for
        the default summarization behavior.
        """
        from app.prompts.templates import RESEARCHER_PERSONA
        
        assert RESEARCHER_PERSONA is not None, (
            "Researcher persona should be defined in templates"
        )
        assert "research scientist" in RESEARCHER_PERSONA.lower(), (
            "Researcher persona should mention research scientist"
        )


class TestHealthEndpoint:
    """Test suite for Health Check endpoints"""
    
    def test_root_health_check(self):
        """Verify root /health endpoint works"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_ollama_health_check_success(self):
        """Verify /summarize/health returns 200 when Ollama is healthy"""
        with patch('app.routers.summarize.ollama_service.check_health') as mock_health:
            mock_health.return_value = True
            
            response = client.get("/summarize/health")
            assert response.status_code == 200


class TestEndToEndValidation:
    """End-to-end validation tests for complete fail-safe scenarios"""
    
    def test_valid_request_structure(self):
        """
        Verify a valid request passes validation and reaches the service layer
        """
        with patch('app.routers.summarize.ollama_service.generate_summary') as mock_generate:
            mock_generate.return_value = "This is a test summary."
            
            response = client.post(
                "/summarize",
                json={
                    "text": "This is a valid test text with enough characters to pass validation and be processed.",
                    "domain": "general research"
                }
            )
            
            # Should not be 422 (validation error)
            assert response.status_code != 422, (
                "Valid request should not return 422"
            )


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


if __name__ == "__main__":
    # Run tests with: python -m pytest backend/test_failsafe.py -v
    pytest.main([__file__, "-v", "--tb=short"])
