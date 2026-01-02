"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class TicketInput(BaseModel):
    """Input schema for ticket classification request."""
    text: str = Field(..., min_length=1, description="The text content to classify")


class Prediction(BaseModel):
    """Schema for a single prediction with label and confidence score."""
    label: str = Field(..., description="Predicted intent/classification label")
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score (probability) of the prediction")


class AnalysisResult(BaseModel):
    """Schema for analysis result."""
    language: str = Field(..., description="Detected language code (e.g., 'tr', 'en')")
    intent: str = Field(..., description="Top predicted intent/classification label (for backward compatibility)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the top prediction (for backward compatibility)")
    predictions: List[Prediction] = Field(..., description="Top 3 predicted labels with their confidence scores")
    sanitized_text: Optional[str] = Field(None, description="PII-masked version of the input text")
    response_text: Optional[str] = Field(None, description="Generated natural language response")
    translated_text: Optional[str] = Field(None, description="English translation of the text (if original was Turkish)")


class TicketHistory(BaseModel):
    """Schema for ticket history item."""
    id: int = Field(..., description="Ticket ID")
    text: str = Field(..., description="Original ticket text")
    sanitized_text: Optional[str] = Field(None, description="PII-masked version of the input text")
    intent: str = Field(..., description="Predicted intent")
    confidence: float = Field(..., description="Confidence score")
    language: str = Field(..., description="Detected language")
    response_text: Optional[str] = Field(None, description="Generated response")
    translated_text: Optional[str] = Field(None, description="English translation of the text (if original was Turkish)")
    created_at: str = Field(..., description="Creation timestamp")


class StatsResponse(BaseModel):
    """Schema for statistics response."""
    total_tickets: int = Field(..., description="Total number of processed tickets")
    active_tasks: int = Field(..., description="Number of active/pending tasks")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate (0.0 to 1.0)")


class TaskResponse(BaseModel):
    """Response schema for task creation."""
    task_id: str = Field(..., description="Celery task ID for tracking the async job")
    status: str = Field(..., description="Current task status")
    message: str = Field(..., description="Human-readable status message")


class TaskStatusResponse(BaseModel):
    """Response schema for task status check."""
    task_id: str = Field(..., description="Celery task ID")
    status: TaskStatus = Field(..., description="Current task status")
    result: Optional[AnalysisResult] = Field(None, description="Analysis result if task is completed")
    error: Optional[str] = Field(None, description="Error message if task failed")




