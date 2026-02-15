"""
LLM-based key field extraction using LangChain.
Extracts structured fields from documents based on their classified type.
"""

import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.pipeline._llm import get_llm


# Type-specific extraction prompts
FIELD_PROMPTS = {
    "invoice": """Extract the following fields from this invoice document.
Return ONLY a valid JSON object (no markdown, no extra text):
{{
    "vendor_name": "name of the vendor/supplier",
    "invoice_number": "invoice/bill number",
    "invoice_date": "date of the invoice",
    "due_date": "payment due date or null",
    "total_amount": "total amount with currency",
    "line_items": ["list of items/services"],
    "payment_terms": "payment terms if mentioned or null"
}}""",

    "report": """Extract the following fields from this report document.
Return ONLY a valid JSON object (no markdown, no extra text):
{{
    "title": "report title",
    "author": "author name or null",
    "date": "report date",
    "department": "department or team or null",
    "key_findings": ["list of main findings or conclusions"],
    "recommendations": ["list of recommendations if any"]
}}""",

    "hr_form": """Extract the following fields from this HR document.
Return ONLY a valid JSON object (no markdown, no extra text):
{{
    "employee_name": "name of the employee",
    "employee_id": "employee ID or null",
    "department": "department name",
    "form_type": "type of HR form (leave, onboarding, etc.)",
    "date": "form date",
    "status": "approved/pending/rejected or null",
    "details": "brief description of the form purpose"
}}""",

    "legal_document": """Extract the following fields from this legal document.
Return ONLY a valid JSON object (no markdown, no extra text):
{{
    "document_title": "title of the legal document",
    "parties_involved": ["list of parties"],
    "effective_date": "effective/start date",
    "expiry_date": "expiry/end date or null",
    "key_clauses": ["list of key clauses or terms"],
    "governing_law": "governing law/jurisdiction or null"
}}""",

    "other": """Extract any relevant structured information from this document.
Return ONLY a valid JSON object (no markdown, no extra text):
{{
    "title": "document title or subject",
    "date": "any date mentioned or null",
    "author": "author or creator or null",
    "key_points": ["list of main points or information"],
    "category_suggestion": "your best guess at what type of document this is"
}}""",
}


def extract_fields(text: str, doc_type: str) -> dict:
    """
    Extract structured key fields from a document using an LLM.
    
    Args:
        text: The extracted document text.
        doc_type: The classified document type.
    
    Returns:
        Dict of extracted fields.
    """
    llm = get_llm()

    system_prompt = FIELD_PROMPTS.get(doc_type, FIELD_PROMPTS["other"])

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Extract fields from this document:\n\n{text}")
    ])

    # Truncate long documents
    truncated = text[:5000] if len(text) > 5000 else text

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"text": truncated})

    try:
        cleaned = response.strip()
        # Strip markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

        return json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        return {"raw_extraction": response.strip(), "parse_error": True}
