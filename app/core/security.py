"""Security utilities for API key validation."""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from the request header.
    
    Args:
        api_key: The API key from the X-API-Key header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide X-API-Key header."
        )
    
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key."
        )
    
    return api_key




