"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.core.db import Base


class Ticket(Base):
    """Ticket model for storing processed ticket data."""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False, comment="Original ticket text")
    sanitized_text = Column(Text, nullable=True, comment="PII-masked version of the input text")
    intent = Column(String(255), nullable=False, comment="Predicted intent/classification")
    confidence = Column(Float, nullable=False, comment="Confidence score of prediction")
    language = Column(String(10), nullable=False, comment="Detected language code")
    response_text = Column(Text, nullable=True, comment="Generated response text")
    translated_text = Column(Text, nullable=True, comment="English translation of the text (if original was Turkish)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, intent='{self.intent}', language='{self.language}')>"

