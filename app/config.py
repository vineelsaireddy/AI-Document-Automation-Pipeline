"""
Application configuration — loads settings from .env file.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider: "openai", "gemini", or "groq"
    LLM_PROVIDER: str = "groq"

    # API Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./doc_pipeline.db"

    # Webhook
    WEBHOOK_SECRET: str = "your-webhook-secret-here"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Model names
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GEMINI_MODEL: str = "gemini-1.5-flash-latest"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
