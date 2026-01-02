"""FastAPI main application."""
import logging
import traceback
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from celery.result import AsyncResult
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.core.security import verify_api_key
from app.models.schemas import (
    TicketInput,
    TaskResponse,
    TaskStatusResponse,
    TaskStatus,
    AnalysisResult,
    Prediction,
    TicketHistory,
    StatsResponse
)
from app.worker.tasks import process_ticket_task
from app.services.guardrails import sanitize_text
from app.services.model_manager import model_manager
from app.core.db import get_db, init_db
from app.models.sql_models import Ticket

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Add rate limit exception handler with custom JSON response
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom exception handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "message": "You have exceeded the rate limit of 5 requests per minute. Please try again later.",
            "retry_after": exc.retry_after if hasattr(exc, 'retry_after') else None
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize models and database on application startup.
    
    CRITICAL: This function must NOT raise exceptions, otherwise Cloud Run
    will kill the container. The server MUST start listening on the port.
    """
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.warning("Server will continue to start despite database initialization failure")
        # DO NOT raise - allow server to start
    
    logger.info("Loading ML models...")
    try:
        model_manager.load_models()
        logger.info("Models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load models: {str(e)}")
        logger.warning("Server will continue to start despite model loading failure (lazy loading will be used)")
        # DO NOT raise - allow server to start (models will lazy-load on first request)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "message": "SmartSupport Backend API",
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": model_manager.english_model is not None,
        "translation_enabled": True  # Turkish uses translation layer
    }


@app.post(
    f"{settings.API_V1_PREFIX}/tickets",
    response_model=TaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Tickets"]
)
@limiter.limit("5/minute")
async def create_ticket(
    request: Request,
    ticket: TicketInput,
    api_key: str = Depends(verify_api_key)
) -> TaskResponse:
    """
    Create a new ticket classification task.
    
    - Validates API key
    - Sanitizes input text (masks PII)
    - Triggers async Celery task
    - Returns task ID for status tracking
    """
    try:
        # Sanitize text before processing
        sanitized_text = sanitize_text(ticket.text)
        
        # Trigger async task
        task = process_ticket_task.delay(sanitized_text)
        
        logger.info(f"Created task {task.id} for ticket classification")
        
        return TaskResponse(
            task_id=task.id,
            status="PENDING",
            message="Ticket classification task created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating ticket task: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket task: {str(e)}"
        )


@app.get(
    f"{settings.API_V1_PREFIX}/tickets/status/{{task_id}}",
    response_model=TaskStatusResponse,
    tags=["Tickets"]
)
async def get_ticket_status(
    task_id: str,
    api_key: str = Depends(verify_api_key)
) -> TaskStatusResponse:
    """
    Get the status and result of a ticket classification task.
    
    - Validates API key
    - Checks Celery task status
    - Returns result if task is completed
    """
    try:
        task_result = AsyncResult(task_id, app=process_ticket_task.app)
        
        # Map Celery states to our TaskStatus enum
        status_mapping = {
            "PENDING": TaskStatus.PENDING,
            "STARTED": TaskStatus.STARTED,
            "SUCCESS": TaskStatus.SUCCESS,
            "FAILURE": TaskStatus.FAILURE,
            "RETRY": TaskStatus.RETRY,
            "REVOKED": TaskStatus.REVOKED,
        }
        
        task_status = status_mapping.get(task_result.state, TaskStatus.PENDING)
        
        response = TaskStatusResponse(
            task_id=task_id,
            status=task_status,
            result=None,
            error=None
        )
        
        if task_result.ready():
            if task_result.successful():
                # Task completed successfully
                result_data = task_result.result
                
                # Convert predictions list to Prediction objects
                predictions_data = result_data.get("predictions", [])
                predictions = [
                    Prediction(label=pred.get("label", "unknown"), score=pred.get("score", 0.0))
                    for pred in predictions_data
                ]
                
                response.result = AnalysisResult(
                    language=result_data.get("language", "unknown"),
                    intent=result_data.get("intent", "unknown"),
                    confidence=result_data.get("confidence", 0.0),
                    predictions=predictions,
                    sanitized_text=result_data.get("sanitized_text"),
                    response_text=result_data.get("response_text"),
                    translated_text=result_data.get("translated_text"),
                    prediction_details=result_data.get("prediction_details")
                )
            else:
                # Task failed
                response.error = str(task_result.info) if task_result.info else "Task failed with unknown error"
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check task status: {str(e)}"
        )


@app.get(
    f"{settings.API_V1_PREFIX}/stats",
    response_model=StatsResponse,
    tags=["Statistics"]
)
async def get_stats(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
) -> StatsResponse:
    """
    Get system statistics.
    
    - Validates API key
    - Returns total tickets, active tasks, and success rate
    """
    try:
        # Count total tickets in database
        total_tickets = db.query(func.count(Ticket.id)).scalar() or 0
        
        active_tasks = 0
        
        # Calculate success rate (tickets with confidence > 0.5 are considered successful)
        successful_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.confidence > 0.5
        ).scalar() or 0
        
        success_rate = (successful_tickets / total_tickets) if total_tickets > 0 else 0.0
        
        return StatsResponse(
            total_tickets=total_tickets,
            active_tasks=active_tasks,
            success_rate=success_rate
        )
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@app.get(
    f"{settings.API_V1_PREFIX}/history",
    response_model=List[TicketHistory],
    tags=["History"]
)
async def get_history(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
    limit: int = 10
) -> List[TicketHistory]:
    """
    Get ticket processing history.
    
    - Validates API key
    - Returns the last N processed tickets (default: 10)
    """
    try:
        # Get last N tickets ordered by creation date
        tickets = db.query(Ticket).order_by(
            Ticket.created_at.desc()
        ).limit(limit).all()
        
        logger.info(f"Found {len(tickets)} tickets in database (requested limit: {limit})")
        
        return [
            TicketHistory(
                id=ticket.id,
                text=ticket.text,
                sanitized_text=ticket.sanitized_text if hasattr(ticket, 'sanitized_text') else ticket.text,
                intent=ticket.intent,
                confidence=ticket.confidence,
                language=ticket.language,
                response_text=ticket.response_text,
                translated_text=ticket.translated_text,
                prediction_details=getattr(ticket, 'prediction_details', None),
                created_at=ticket.created_at.isoformat() if ticket.created_at else ""
            )
            for ticket in tickets
        ]
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get history: {str(e)}"
        )


@app.get(
    f"{settings.API_V1_PREFIX}/debug/db",
    tags=["Debug"]
)
async def debug_database(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """
    Debug endpoint to check database status and contents.
    Useful for troubleshooting without rebuilding containers.
    """
    import traceback
    from app.core.db import DATABASE_PATH, DATABASE_URL
    from pathlib import Path
    
    try:
        # Check if database file exists
        db_exists = DATABASE_PATH.exists() if DATABASE_PATH else False
        db_size = DATABASE_PATH.stat().st_size if db_exists else 0
        
        # Count tickets
        total_count = db.query(func.count(Ticket.id)).scalar() or 0
        
        # Get sample tickets
        sample_tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).limit(5).all()
        
        return {
            "database_path": str(DATABASE_PATH),
            "database_url": DATABASE_URL,
            "database_exists": db_exists,
            "database_size_bytes": db_size,
            "total_tickets": total_count,
            "sample_tickets": [
                {
                    "id": t.id,
                    "intent": t.intent,
                    "language": t.language,
                    "sanitized_text": getattr(t, 'sanitized_text', t.text),
                    "prediction_details": getattr(t, 'prediction_details', None),
                    "translated_text": t.translated_text,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in sample_tickets
            ],
            "status": "ok"
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "status": "error"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




