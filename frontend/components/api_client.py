"""
API Client for communicating with the backend
"""
import os
import requests

# Get API_HOST from environment variable
API_HOST = os.getenv("API_HOST","http://api:8000")#http://localhost:8000")


def call_backend_api(text: str) -> dict:
    """
    Call the backend API to analyze strata.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary containing the API response
    """
    endpoint = f"{API_HOST}/summarize"
    try:
        response = requests.post(
            endpoint,
            json={"text": text},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Unable to connect to the backend API. Please ensure the service is running."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
