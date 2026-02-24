"""
FastAPI application entry point.
Configures CORS, static files, routers, and database initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.database import init_db
from app.routers import documents, webhook, dashboard

# Initialize FastAPI app
app = FastAPI(
    title="AI Document Automation Pipeline",
    description=(
        "An LLM-powered document processing pipeline that automates extraction, "
        "classification, and summarization of business documents using LangChain, "
        "LangGraph, and OpenAI/Gemini APIs."
    ),
    version="1.0.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(documents.router)
app.include_router(webhook.router)
app.include_router(dashboard.router)

# Serve frontend static files
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.on_event("startup")
def on_startup():
    """Initialize the database tables on application startup."""
    init_db()
    print("✅ Database initialized.")
    print("📄 AI Document Automation Pipeline is running!")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 API Docs:  http://localhost:8000/docs")


@app.get("/")
async def serve_dashboard():
    """Serve the frontend dashboard."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "AI Document Automation Pipeline API", "docs": "/docs"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Document Automation Pipeline"}
