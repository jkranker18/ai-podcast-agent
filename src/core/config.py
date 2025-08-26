"""
Configuration management for the AI Podcast Agent.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///data/db.sqlite"
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_user: str = ""
    email_password: str = ""
    recipient_email: str = ""  # Legacy single recipient
    subscriber_emails: str = ""  # Comma-separated list of subscribers
    email_enabled: bool = False
    
    # Slack settings
    slack_bot_token: str = ""
    slack_channel: str = ""
    slack_enabled: bool = False
    
    # AI Model settings
    local_llm_model: str = "llama3.1:8b"  # Ollama model name
    whisper_model: str = "base"  # Whisper model size: tiny, base, small, medium, large
    embedding_model: str = "all-MiniLM-L6-v2"  # Sentence transformers model
    
    # OpenAI settings (for fallback)
    openai_api_key: str = ""
    
    # Storage paths
    audio_storage_path: str = "data/audio"
    transcript_storage_path: str = "data/transcripts"
    summary_storage_path: str = "data/summaries"
    embedding_storage_path: str = "data/embeddings"
    
    # Processing settings
    max_concurrent_downloads: int = 3
    max_concurrent_transcriptions: int = 2  # Lower for CPU-intensive transcription
    max_concurrent_summaries: int = 2
    batch_size: int = 10
    
    # Scheduling settings
    feed_check_interval_hours: int = 6
    digest_send_time: str = "08:00"
    digest_timezone: str = "UTC"
    
    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/podcast_agent.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def model_post_init(self, __context):
        """Create necessary directories after initialization."""
        import os
        from pathlib import Path
        
        # Create storage directories
        for path in [
            self.audio_storage_path,
            self.transcript_storage_path,
            self.summary_storage_path,
            self.embedding_storage_path,
            "logs"
        ]:
            Path(path).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings() 