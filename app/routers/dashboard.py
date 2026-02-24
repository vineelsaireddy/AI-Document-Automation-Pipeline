"""
Dashboard/reporting API routes.
GET /api/dashboard/stats — aggregate statistics for the reporting dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Document
from app.schemas import DashboardStats, DocumentResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Return aggregate statistics for the reporting dashboard:
    - Total documents processed
    - Count by status (completed, failed, pending)
    - Classification breakdown (invoice, report, hr_form, etc.)
    - 5 most recent documents
    """
    total = db.query(Document).count()
    completed = db.query(Document).filter(Document.status == "completed").count()
    failed = db.query(Document).filter(Document.status == "failed").count()
    pending = db.query(Document).filter(
        Document.status.in_(["pending", "processing"])
    ).count()

    # Classification breakdown
    type_counts = (
        db.query(Document.doc_type, func.count(Document.id))
        .filter(Document.doc_type.isnot(None))
        .group_by(Document.doc_type)
        .all()
    )
    classification_breakdown = {
        doc_type: count for doc_type, count in type_counts if doc_type
    }

    # Recent documents
    recent = (
        db.query(Document)
        .order_by(Document.upload_time.desc())
        .limit(5)
        .all()
    )

    return DashboardStats(
        total_documents=total,
        completed=completed,
        failed=failed,
        pending=pending,
        classification_breakdown=classification_breakdown,
        recent_documents=recent,
    )
