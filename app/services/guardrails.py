"""PII masking and text sanitization service using Microsoft Presidio."""
import re
import logging
from typing import List
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

logger = logging.getLogger(__name__)


class PIIGuardrail:
    """
    PII Guardrail using Microsoft Presidio for context-aware anonymization.
    Provides robust PII detection and masking with custom Turkish ID (TCKN) support.
    """
    
    def __init__(self):
        """Initialize Presidio analyzer and anonymizer engines."""
        try:
            # Initialize analyzer engine
            self.analyzer = AnalyzerEngine()
            
            # Add custom PatternRecognizer for Turkish ID (TCKN)
            # TCKN: 11 digits, first digit must be 1-9
            tckn_pattern = Pattern(
                name="TCKN",
                regex=r"\b[1-9][0-9]{10}\b",
                score=0.9
            )
            
            tckn_recognizer = PatternRecognizer(
                supported_entity="TCKN",
                patterns=[tckn_pattern],
                context=["kimlik", "TCKN", "türk", "turkish", "identity", "id number"]
            )
            
            # Add custom recognizer to analyzer
            self.analyzer.registry.add_recognizer(tckn_recognizer)
            logger.info("PIIGuardrail initialized with Presidio engines and custom TCKN recognizer")
            
            # Initialize anonymizer engine
            self.anonymizer = AnonymizerEngine()
            
        except Exception as e:
            logger.error(f"Failed to initialize PIIGuardrail: {str(e)}")
            raise
    
    def anonymize(self, text: str) -> str:
        """
        Anonymize PII in the given text using Presidio.
        
        Detects and masks:
        - PHONE_NUMBER
        - EMAIL_ADDRESS
        - CREDIT_CARD
        - CRYPTO
        - IP_ADDRESS
        - TCKN (Turkish ID - custom recognizer)
        
        Args:
            text: Input text containing potentially sensitive information
            
        Returns:
            Anonymized text with PII masked (e.g., <PHONE_NUMBER>, <EMAIL_ADDRESS>)
        """
        if not text or not text.strip():
            return text
        
        try:
            # Configure analyzer to look for specific PII types
            # Note: Presidio will detect all supported entities, but we can filter if needed
            supported_entities = [
                "PHONE_NUMBER",
                "EMAIL_ADDRESS",
                "CREDIT_CARD",
                "CRYPTO",
                "IP_ADDRESS",
                "TCKN"  # Custom Turkish ID recognizer
            ]
            
            # Analyze text for PII entities
            analyzer_results = self.analyzer.analyze(
                text=text,
                language="en",  # Presidio works best with English, but will detect patterns in any language
                entities=supported_entities
            )
            
            if not analyzer_results:
                logger.debug("No PII entities detected in text")
                return text
            
            # Anonymize detected entities
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results
            )
            
            masked_text = anonymized_result.text
            logger.debug(f"Anonymized text: {len(analyzer_results)} PII entities detected and masked")
            
            return masked_text
            
        except Exception as e:
            logger.error(f"Error in PII anonymization: {str(e)}")
            # Fallback: return original text if anonymization fails
            # In production, you might want to raise or use a simpler fallback
            logger.warning("Falling back to original text due to anonymization error")
            return text


# Global instance - initialized once to avoid reloading models
_guardrail_instance: PIIGuardrail = None


def get_guardrail() -> PIIGuardrail:
    """
    Get or create the global PIIGuardrail instance.
    Singleton pattern to avoid reloading Presidio models on every call.
    
    Returns:
        PIIGuardrail instance
    """
    global _guardrail_instance
    
    if _guardrail_instance is None:
        logger.info("Initializing global PIIGuardrail instance...")
        _guardrail_instance = PIIGuardrail()
    
    return _guardrail_instance


# Backward compatibility function
def sanitize_text(text: str) -> str:
    """
    Backward compatibility wrapper for sanitize_text function.
    Uses the new PIIGuardrail system.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        Sanitized text with PII masked
    """
    guardrail = get_guardrail()
    return guardrail.anonymize(text)
