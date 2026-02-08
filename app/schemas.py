"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


# --- Response Schemas ---

class DocumentResponse(BaseModel):
    """Response schema for a single document."""
    id: int
    filename: str
    upload_time: Optional[datetime] = None
    doc_type: Optional[str] = None
    confidence: Optional[float] = None
    summary: Optional[str] = None
    extracted_fields: Optional[dict] = None
    status: str
    error_message: Optional[str] = None
    source: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Response schema for paginated document list."""
    total: int
    documents: list[DocumentResponse]


class DashboardStats(BaseModel):
    """Response schema for dashboard statistics."""
    total_documents: int
    completed: int
    failed: int
    pending: int
    classification_breakdown: dict[str, int]
    recent_documents: list[DocumentResponse]


# --- Request Schemas ---

class WebhookPayload(BaseModel):
    """Request schema for webhook ingestion."""
    filename: str
    content_base64: str
    webhook_secret: Optional[str] = None


class ProcessingResult(BaseModel):
    """Internal schema for pipeline output."""
    raw_text: str
    doc_type: str
    confidence: float
    summary: str
    extracted_fields: dict[str, Any]
    status: str = "completed"
    error_message: Optional[str] = None
