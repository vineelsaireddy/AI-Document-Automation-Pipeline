"""
SQLAlchemy ORM models for the document pipeline.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """Stores a processed document with its classification, extracted fields, and summary."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    raw_text = Column(Text, nullable=False)
    doc_type = Column(String(50), nullable=True)           # invoice, report, hr_form, legal_document, other
    confidence = Column(Float, nullable=True)               # classification confidence 0-1
    summary = Column(Text, nullable=True)
    extracted_fields = Column(JSON, nullable=True)           # structured key-value data
    status = Column(String(20), default="pending")           # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    source = Column(String(20), default="upload")            # upload or webhook

    def to_dict(self):
        """Serialize to dictionary for JSON responses."""
        return {
            "id": self.id,
            "filename": self.filename,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "doc_type": self.doc_type,
            "confidence": self.confidence,
            "summary": self.summary,
            "extracted_fields": self.extracted_fields,
            "status": self.status,
            "error_message": self.error_message,
            "source": self.source,
        }
