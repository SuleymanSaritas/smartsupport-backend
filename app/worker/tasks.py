"""Celery tasks for async ticket processing."""
import json
import logging
import traceback
from app.worker.celery_app import celery_app
from app.services.model_manager import model_manager
from app.services.response_generator import generate_response
from app.services.guardrails import get_guardrail
from app.core.db import SessionLocal
from app.models.sql_models import Ticket

logger = logging.getLogger(__name__)

# Initialize PII guardrail globally (so we don't reload the model on every task)
guardrail = get_guardrail()


@celery_app.task(bind=True, name="process_ticket_task")
def process_ticket_task(self, text: str) -> dict:
    """
    Async Celery task to process ticket classification.
    
    Args:
        text: Sanitized input text to classify (PII already masked)
        
    Returns:
        Dictionary with analysis results including language, intent, confidence, sanitized_text, and response_text
    """
    task_id = self.request.id
    db = SessionLocal()
    
    try:
        # Mask PII using Presidio guardrail BEFORE processing or saving
        logger.info(f"Task {task_id} - Masking PII...")
        masked_text = guardrail.anonymize(text)
        logger.info(f"Task {task_id} - PII masking complete")
        
        # Run model prediction on masked text
        # Note: ModelManager will lazy-load models if not already loaded (for worker processes)
        logger.info(f"Task {task_id} - Starting prediction...")
        result = model_manager.predict(masked_text)
        
        # Extract prediction data
        intent = result.get("intent", "unknown")
        confidence = result.get("confidence", 0.0)
        language = result.get("language", "en")
        translated_text = result.get("translated_text", None)
        predictions = result.get("predictions", [])  # Get top 3 predictions list
        
        logger.info(f"Task {task_id} - Prediction complete: intent={intent}, confidence={confidence:.3f}, language={language}")
        if translated_text:
            logger.info(f"Task {task_id} - Translation: {translated_text[:50]}...")
        
        # Convert predictions list to JSON string for storage
        prediction_details_json = json.dumps(predictions) if predictions else None
        logger.debug(f"Task {task_id} - Top 3 predictions: {prediction_details_json}")
        
        # Generate varied response based on intent and language
        response_text = generate_response(intent, language)
        logger.info(f"Task {task_id} - Generated response: {response_text[:50]}...")
        
        # Add masked text and response to result
        result["sanitized_text"] = masked_text  # Use masked text, not original
        result["response_text"] = response_text
        result["prediction_details"] = prediction_details_json  # Add JSON string to result
        
        # Save ticket to database with explicit logging
        # IMPORTANT: Save masked_text to DB, not original text
        logger.info(f"Task {task_id} - SAVING TO DB...")
        print(f"Task {task_id} - SAVING TO DB...")
        
        try:
            ticket_entry = Ticket(
                text=masked_text,  # Save masked text to database (PII already anonymized)
                sanitized_text=masked_text,  # Also store in sanitized_text column for API response
                intent=intent,
                confidence=confidence,
                language=language,
                response_text=response_text,
                translated_text=translated_text,  # Store the English translation
                prediction_details=prediction_details_json  # Store top 3 predictions as JSON string
            )
            
            db.add(ticket_entry)
            db.commit()
            db.refresh(ticket_entry)
            
            logger.info(f"✅ Ticket {task_id} saved to DB successfully with ID: {ticket_entry.id}")
            print(f"✅ Ticket {task_id} saved to DB successfully with ID: {ticket_entry.id}")
            
        except Exception as db_error:
            db.rollback()
            error_msg = f"❌ DB Save Error for task {task_id}: {str(db_error)}"
            logger.error(error_msg)
            print(error_msg)
            logger.error(f"Full DB error traceback:\n{traceback.format_exc()}")
            # Don't fail the task if DB save fails, just log it
        
        logger.info(f"Task {task_id} completed successfully")
        return result
        
    except Exception as e:
        # Log full traceback for debugging
        error_traceback = traceback.format_exc()
        logger.error(
            f"Task {task_id} failed with error: {str(e)}\n"
            f"Full traceback:\n{error_traceback}"
        )
        # Retry logic can be added here if needed
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        db.close()
        logger.debug(f"Task {task_id} - Database session closed")
