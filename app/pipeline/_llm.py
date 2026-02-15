"""
LLM provider factory — returns the appropriate LangChain chat model
based on configuration (OpenAI or Google Gemini).
"""

from langchain_core.language_models import BaseChatModel
from app.config import settings


def get_llm() -> BaseChatModel:
    """
    Return a LangChain chat model based on the configured LLM_PROVIDER.
    
    Supports:
        - "openai" → ChatOpenAI (requires OPENAI_API_KEY)
        - "gemini" → ChatGoogleGenerativeAI (requires GOOGLE_API_KEY)
    
    Returns:
        A LangChain BaseChatModel instance.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("sk-your"):
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY in your .env file."
            )
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,
        )
    
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY.startswith("your-google"):
            raise ValueError(
                "Google API key not configured. "
                "Set GOOGLE_API_KEY in your .env file."
            )
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,
        )
    
    elif provider == "groq":
        from langchain_groq import ChatGroq

        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY.startswith("your-groq"):
            raise ValueError(
                "Groq API key not configured. "
                "Set GROQ_API_KEY in your .env file."
            )
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1,
        )
    
    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER: '{provider}'. "
            "Use 'openai', 'gemini', or 'groq'."
        )
