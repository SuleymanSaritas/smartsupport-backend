"""Unit tests for FastAPI endpoints."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# Create test client
client = TestClient(app)


def test_read_root():
    """Test that GET / returns 200 and welcome message."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "healthy"
    assert "SmartSupport" in data["message"]


def test_create_ticket():
    """Test POST /api/v1/tickets endpoint."""
    # Mock Celery task to avoid actual async processing
    mock_task = MagicMock()
    mock_task.id = "test-task-id-123"
    
    with patch('app.main.process_ticket_task.delay', return_value=mock_task):
        payload = {"text": "My internet connection is lost, help!"}
        headers = {"X-API-Key": settings.API_KEY}
        
        response = client.post(
            f"{settings.API_V1_PREFIX}/tickets",
            json=payload,
            headers=headers
        )
        
        # Verify status code is 202 (Accepted) for async task
        # Note: User requested 200, but endpoint correctly returns 202 for async operations
        assert response.status_code == 202
        
        # Verify response JSON structure
        data = response.json()
        assert "task_id" in data  # Note: API returns "task_id", not "id"
        assert "status" in data
        assert "message" in data
        
        # Note: "intent" is not in initial response, it's available after task completes
        # via GET /api/v1/tickets/status/{task_id}
        
        # Verify task_id matches mocked task
        assert data["task_id"] == "test-task-id-123"
        assert data["status"] == "PENDING"


def test_create_ticket_missing_api_key():
    """Test that POST /api/v1/tickets requires API key."""
    payload = {"text": "Test ticket"}
    
    response = client.post(
        f"{settings.API_V1_PREFIX}/tickets",
        json=payload
        # No API key header
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_create_ticket_invalid_api_key():
    """Test that POST /api/v1/tickets rejects invalid API key."""
    payload = {"text": "Test ticket"}
    headers = {"X-API-Key": "invalid-key"}
    
    response = client.post(
        f"{settings.API_V1_PREFIX}/tickets",
        json=payload,
        headers=headers
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_rate_limit():
    """Test that rate limiting works (5 requests per minute)."""
    # Mock Celery task
    mock_task = MagicMock()
    mock_task.id = "test-task-id"
    
    payload = {"text": "Test rate limit"}
    headers = {"X-API-Key": settings.API_KEY}
    
    with patch('app.main.process_ticket_task.delay', return_value=mock_task):
        # Make 5 requests - all should succeed
        for i in range(5):
            response = client.post(
                f"{settings.API_V1_PREFIX}/tickets",
                json=payload,
                headers=headers
            )
            assert response.status_code == 202, f"Request {i+1} should succeed"
        
        # 6th request should be rate limited
        response = client.post(
            f"{settings.API_V1_PREFIX}/tickets",
            json=payload,
            headers=headers
        )
        
        assert response.status_code == 429, "6th request should be rate limited"
        data = response.json()
        assert "error" in data or "detail" in data
        assert "rate limit" in str(data).lower()


def test_health_check():
    """Test GET /health endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "models_loaded" in data
    assert "translation_enabled" in data

