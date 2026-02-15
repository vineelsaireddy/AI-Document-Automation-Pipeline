"""
LLM-based document summarization using LangChain.
Generates concise 2-3 sentence summaries of documents.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.pipeline._llm import get_llm


SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a document summarization expert. Generate a concise, professional 
summary of the given document in exactly 2-3 sentences. 

The summary should:
- Capture the main purpose and key information of the document
- Include any critical dates, amounts, or names mentioned
- Be written in a professional, business-appropriate tone

Return ONLY the summary text, nothing else."""),
    ("human", "Summarize this {doc_type} document:\n\n{text}")
])


def summarize_document(text: str, doc_type: str) -> str:
    """
    Generate a concise summary of a document using an LLM.
    
    Args:
        text: The extracted document text.
        doc_type: The classified document type (provides context).
    
    Returns:
        A 2-3 sentence summary string.
    """
    llm = get_llm()

    # Truncate long documents
    truncated = text[:5000] if len(text) > 5000 else text

    chain = SUMMARY_PROMPT | llm | StrOutputParser()
    summary = chain.invoke({"text": truncated, "doc_type": doc_type})

    return summary.strip()
