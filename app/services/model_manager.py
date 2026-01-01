"""Model manager singleton for loading and managing ML models."""
import logging
from typing import Dict, Any, List
from langdetect import detect, LangDetectException
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from deep_translator import GoogleTranslator
import torch
import torch.nn.functional as F
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton class to manage ML models for intent classification.
    Uses translation layer for Turkish: translates to English, then uses English model.
    This approach provides better accuracy than using a separate Turkish model.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize models if not already done."""
        if not ModelManager._initialized:
            # Turkish model removed - using translation layer instead
            self.turkish_tokenizer = None
            self.turkish_model = None
            self.english_tokenizer = None
            self.english_model = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            ModelManager._initialized = True
            logger.info(f"ModelManager initialized. Using device: {self.device}")
    
    def load_models(self):
        """
        Load English model only (Turkish model removed - using translation instead).
        This method is idempotent - it will not reload models if they are already loaded.
        """
        # Check if model is already loaded (idempotent check)
        if self.english_model is not None:
            logger.debug("English model already loaded, skipping reload")
            return
        
        try:
            # Turkish model loading removed - we use translation layer instead
            # This saves RAM and improves accuracy
            logger.info("Turkish model removed - using translation layer instead")
            
            logger.info("Loading English model...")
            self.english_tokenizer = AutoTokenizer.from_pretrained(settings.ENGLISH_MODEL)
            self.english_model = AutoModelForSequenceClassification.from_pretrained(
                settings.ENGLISH_MODEL
            )
            self.english_model.to(self.device)
            self.english_model.eval()
            logger.info("English model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def predict(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Predict intent classification for the given text.
        
        Implements translation layer for Turkish:
        1. Detect language
        2. If Turkish, translate to English
        3. Use English model for all predictions
        4. Return original language in response (for Turkish response generation)
        
        Implements lazy loading: if models are not loaded, they will be loaded automatically.
        This is especially important for Celery workers that run in separate processes.
        
        Args:
            text: Input text to classify
            top_k: Number of top predictions to return (default: 3)
            
        Returns:
            Dictionary with 'language', 'intent', 'confidence', and 'predictions' keys
            where 'predictions' is a list of top_k predictions with labels and scores
            Note: 'language' will be the original detected language (e.g., 'tr' for Turkish)
            
        Raises:
            ValueError: If language detection fails or models cannot be loaded
        """
        # Lazy loading: Check if model is loaded, if not, load it
        if self.english_model is None:
            logger.warning("⚠️ Worker process cache miss. Loading models...")
            self.load_models()
        
        # Detect language
        try:
            detected_lang = detect(text)
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {str(e)}. Defaulting to English.")
            detected_lang = "en"
        
        # Translation layer: If Turkish, translate to English
        text_for_prediction = text
        translated_text = None
        if detected_lang == "tr":
            try:
                logger.debug(f"Translating Turkish text to English: {text[:50]}...")
                translator = GoogleTranslator(source='auto', target='en')
                text_for_prediction = translator.translate(text)
                translated_text = text_for_prediction  # Store the translated text
                logger.debug(f"Translated text: {text_for_prediction[:50]}...")
            except Exception as e:
                logger.warning(f"Translation failed: {str(e)}. Using original text.")
                # Fallback: use original text if translation fails
                text_for_prediction = text
                translated_text = None
        elif detected_lang == "en":
            # For English, translated_text can be the same as original or None
            translated_text = None  # No translation needed for English
        
        # Use English model for all predictions (translated or original)
        # But preserve the original language in the response
        result = self._predict_english(text_for_prediction, detected_lang, top_k)
        
        # Ensure the returned language is the original detected language
        # This is important so the worker knows to generate a Turkish response
        result["language"] = detected_lang
        
        # Add translated text to result
        result["translated_text"] = translated_text
        
        return result
    
    def _predict_english(self, text: str, original_lang: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Run inference using English model and return top K predictions.
        
        Args:
            text: Text to classify (may be translated from Turkish)
            original_lang: Original detected language (preserved in response)
            top_k: Number of top predictions to return
        """
        try:
            inputs = self.english_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.english_model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=-1)
                
                # Get top K predictions
                top_probs, top_indices = torch.topk(probabilities, k=min(top_k, probabilities.size(-1)), dim=-1)
                
                # Get label mapping
                id2label = getattr(self.english_model.config, "id2label", None)
                
                # Build predictions list
                predictions = []
                for i in range(top_k):
                    if i < top_indices.size(-1):
                        idx = top_indices[0][i].item()
                        prob = top_probs[0][i].item()
                        label = id2label[idx] if id2label else f"class_{idx}"
                        predictions.append({
                            "label": label,
                            "score": prob
                        })
                
                # Get top prediction for backward compatibility
                top_idx = top_indices[0][0].item()
                top_prob = top_probs[0][0].item()
                top_label = id2label[top_idx] if id2label else f"class_{top_idx}"
                
                return {
                    "language": original_lang,  # Preserve original language
                    "intent": top_label,
                    "confidence": top_prob,
                    "predictions": predictions
                }
        except Exception as e:
            logger.error(f"Error in English model prediction: {str(e)}")
            raise


# Global instance
model_manager = ModelManager()
