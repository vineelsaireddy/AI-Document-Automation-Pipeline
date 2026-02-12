"""
LLM-based document classifier using LangChain.
Classifies documents into: invoice, report, hr_form, legal_document, other.
"""

import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.pipeline._llm import get_llm

CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a document classification expert. Classify the given document into 
exactly ONE of these categories:

- invoice: Bills, invoices, payment requests, purchase orders
- report: Business reports, analysis documents, research summaries, meeting minutes
- hr_form: HR documents, employee forms, leave applications, onboarding documents
- legal_document: Contracts, agreements, legal notices, compliance documents
- other: Any document that does not fit the above categories

Respond with ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{"category": "<category_name>", "confidence": <0.0_to_1.0>}}

Example response:
{{"category": "invoice", "confidence": 0.92}}"""),
    ("human", "Classify this document:\n\n{text}")
])


def classify_document(text: str) -> dict:
    """
    Classify a document's type using an LLM.
    
    Args:
        text: The extracted document text.
    
    Returns:
        Dict with 'category' (str) and 'confidence' (float).
    """
    llm = get_llm()

    # Truncate very long documents to avoid token limits
    truncated = text[:4000] if len(text) > 4000 else text

    chain = CLASSIFICATION_PROMPT | llm | StrOutputParser()
    response = chain.invoke({"text": truncated})

    try:
        # Clean the response — strip markdown code fences if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
            cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

        result = json.loads(cleaned)
        
        # Validate category
        valid_categories = {"invoice", "report", "hr_form", "legal_document", "other"}
        if result.get("category") not in valid_categories:
            result["category"] = "other"
        
        # Validate confidence
        confidence = float(result.get("confidence", 0.5))
        result["confidence"] = max(0.0, min(1.0, confidence))
        
        return result
    except (json.JSONDecodeError, KeyError, TypeError):
        return {"category": "other", "confidence": 0.3}
