"""
Webhook ingestion endpoint.
POST /api/webhook/ingest — accepts a JSON payload with base64-encoded document.
"""

import base64
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Document
from app.schemas import WebhookPayload, DocumentResponse
from app.pipeline.graph import run_pipeline

router = APIRouter(prefix="/api/webhook", tags=["Webhook"])


@router.post("/ingest", response_model=DocumentResponse)
def webhook_ingest(payload: WebhookPayload, db: Session = Depends(get_db)):
    """
    Webhook endpoint for real-time document ingestion.
    
    Accepts a JSON payload with:
    - filename: Name of the document
    - content_base64: Base64-encoded file content
    - webhook_secret: (optional) Secret for validation
    
    Validates the webhook secret, decodes the content, runs the AI pipeline,
    and stores the result.
    """
    # Validate webhook secret
    if payload.webhook_secret and payload.webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret.")

    # Decode base64 content
    try:
        file_content = base64.b64decode(payload.content_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64-encoded content.")

    if not file_content:
        raise HTTPException(status_code=400, detail="Empty document content.")

    # Create DB record
    doc = Document(
        filename=payload.filename,
        raw_text="",
        status="processing",
        source="webhook",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # Run the processing pipeline
        result = run_pipeline(file_content, payload.filename)

        doc.raw_text = result.get("raw_text", "")
        doc.doc_type = result.get("doc_type", "other")
        doc.confidence = result.get("confidence", 0.0)
        doc.summary = result.get("summary", "")
        doc.extracted_fields = result.get("extracted_fields", {})
        doc.status = result.get("status", "completed")
        doc.error_message = result.get("error_message")

        db.commit()
        db.refresh(doc)

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
        db.refresh(doc)

    return doc
