"""
Document CRUD API routes.
- POST /api/documents/upload — upload and process a document
- GET  /api/documents — list all processed documents
- GET  /api/documents/{id} — get full details of a document
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentListResponse
from app.pipeline.graph import run_pipeline

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload a document file, run it through the AI processing pipeline,
    and store the results in the database.
    
    Supported formats: .pdf, .txt, .docx
    """
    # Validate file type
    allowed_extensions = {".pdf", ".txt", ".docx", ".doc"}
    filename = file.filename or "unknown.txt"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{ext}'. Allowed: {', '.join(allowed_extensions)}",
        )

    # Read file content
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    # Create DB record
    doc = Document(filename=filename, raw_text="", status="processing", source="upload")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        # Run the LangGraph pipeline
        result = run_pipeline(content, filename)

        # Update the record with pipeline results
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


@router.get("", response_model=DocumentListResponse)
def list_documents(
    skip: int = 0,
    limit: int = 20,
    doc_type: str = None,
    db: Session = Depends(get_db),
):
    """List all processed documents with optional type filtering and pagination."""
    query = db.query(Document).order_by(Document.upload_time.desc())

    if doc_type:
        query = query.filter(Document.doc_type == doc_type)

    total = query.count()
    documents = query.offset(skip).limit(limit).all()

    return DocumentListResponse(total=total, documents=documents)


@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(doc_id: int, db: Session = Depends(get_db)):
    """Get full details of a specific processed document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document with id {doc_id} not found.")
    return doc
