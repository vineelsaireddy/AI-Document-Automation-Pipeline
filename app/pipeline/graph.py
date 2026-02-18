"""
LangGraph workflow orchestration.
Wires the document processing pipeline into a state-machine graph:
  Extract Text → Classify → Extract Fields → Summarize
"""

from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END

from app.pipeline.extractor import extract_text
from app.pipeline.classifier import classify_document
from app.pipeline.field_extractor import extract_fields
from app.pipeline.summarizer import summarize_document


# --- State definition ---

class PipelineState(TypedDict):
    """Typed state that flows through the LangGraph pipeline."""
    file_content: bytes
    filename: str
    raw_text: str
    doc_type: str
    confidence: float
    extracted_fields: dict[str, Any]
    summary: str
    status: str
    error_message: Optional[str]


# --- Node functions ---

def extraction_node(state: PipelineState) -> dict:
    """Node 1: Extract raw text from the document file."""
    try:
        raw_text = extract_text(state["file_content"], state["filename"])
        return {"raw_text": raw_text, "status": "extracting"}
    except Exception as e:
        return {
            "raw_text": "",
            "status": "failed",
            "error_message": f"Text extraction failed: {str(e)}",
        }


def classification_node(state: PipelineState) -> dict:
    """Node 2: Classify the document type using the LLM."""
    try:
        result = classify_document(state["raw_text"])
        return {
            "doc_type": result["category"],
            "confidence": result["confidence"],
            "status": "classifying",
        }
    except Exception as e:
        return {
            "doc_type": "other",
            "confidence": 0.0,
            "status": "failed",
            "error_message": f"Classification failed: {str(e)}",
        }


def field_extraction_node(state: PipelineState) -> dict:
    """Node 3: Extract structured key fields based on document type."""
    try:
        fields = extract_fields(state["raw_text"], state["doc_type"])
        return {"extracted_fields": fields, "status": "extracting_fields"}
    except Exception as e:
        return {
            "extracted_fields": {"error": str(e)},
            "status": "failed",
            "error_message": f"Field extraction failed: {str(e)}",
        }


def summarization_node(state: PipelineState) -> dict:
    """Node 4: Generate a concise summary of the document."""
    try:
        summary = summarize_document(state["raw_text"], state["doc_type"])
        return {"summary": summary, "status": "completed"}
    except Exception as e:
        return {
            "summary": "",
            "status": "failed",
            "error_message": f"Summarization failed: {str(e)}",
        }


# --- Conditional edge ---

def should_continue_after_extraction(state: PipelineState) -> str:
    """Route: if text extraction failed, skip to END; otherwise continue."""
    if state.get("status") == "failed" or not state.get("raw_text"):
        return "end"
    return "classify"


def should_continue_after_classification(state: PipelineState) -> str:
    """Route: if classification failed hard, skip to END; otherwise continue."""
    if state.get("status") == "failed":
        return "end"
    return "extract_fields"


# --- Build the graph ---

def build_pipeline() -> StateGraph:
    """
    Construct and compile the LangGraph document processing pipeline.
    
    Pipeline flow:
        extract → (check) → classify → (check) → extract_fields → summarize → END
    
    Returns:
        A compiled LangGraph that can be invoked with PipelineState.
    """
    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("extract", extraction_node)
    graph.add_node("classify", classification_node)
    graph.add_node("extract_fields", field_extraction_node)
    graph.add_node("summarize", summarization_node)

    # Set entry point
    graph.set_entry_point("extract")

    # Add conditional edges
    graph.add_conditional_edges(
        "extract",
        should_continue_after_extraction,
        {"classify": "classify", "end": END},
    )

    graph.add_conditional_edges(
        "classify",
        should_continue_after_classification,
        {"extract_fields": "extract_fields", "end": END},
    )

    # Linear edges
    graph.add_edge("extract_fields", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# Pre-compiled pipeline instance
pipeline = build_pipeline()


def run_pipeline(file_content: bytes, filename: str) -> PipelineState:
    """
    Run the full document processing pipeline.
    
    Args:
        file_content: Raw bytes of the uploaded file.
        filename: Original filename.
    
    Returns:
        Final PipelineState with all extracted data.
    """
    initial_state: PipelineState = {
        "file_content": file_content,
        "filename": filename,
        "raw_text": "",
        "doc_type": "",
        "confidence": 0.0,
        "extracted_fields": {},
        "summary": "",
        "status": "pending",
        "error_message": None,
    }

    result = pipeline.invoke(initial_state)
    return result
