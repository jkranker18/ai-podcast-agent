"""
Database models for the AI Podcast Agent.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Podcast(Base):
    """Podcast feed information."""
    
    __tablename__ = "podcasts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    rss_url = Column(String(500), nullable=False, unique=True)
    website_url = Column(String(500))
    description = Column(Text)
    language = Column(String(10), default="en")
    category = Column(String(100), default="Technology")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    episodes = relationship("Episode", back_populates="podcast")


class Episode(Base):
    """Podcast episode information."""
    
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    published_date = Column(DateTime, nullable=False)
    duration = Column(Integer)  # Duration in seconds
    audio_url = Column(String(500), nullable=False)
    episode_url = Column(String(500))
    guid = Column(String(255), unique=True, nullable=False)
    file_size = Column(Integer)  # File size in bytes
    
    # Processing status
    downloaded = Column(Boolean, default=False)
    transcribed = Column(Boolean, default=False)
    summarized = Column(Boolean, default=False)
    embedded = Column(Boolean, default=False)
    
    # File paths
    audio_file_path = Column(String(500))
    transcript_file_path = Column(String(500))
    summary_file_path = Column(String(500))
    
    # Transcript metadata
    transcript_word_count = Column(Integer)
    transcript_duration = Column(Float)  # Duration in seconds
    transcript_language = Column(String(10))
    transcript_language_probability = Column(Float)
    
    # Processing metadata
    download_started_at = Column(DateTime)
    download_completed_at = Column(DateTime)
    transcription_started_at = Column(DateTime)
    transcription_completed_at = Column(DateTime)
    summarization_started_at = Column(DateTime)
    summarization_completed_at = Column(DateTime)
    
    # Error tracking
    processing_error = Column(Text)
    retry_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    podcast = relationship("Podcast", back_populates="episodes")
    summary = relationship("Summary", back_populates="episode", uselist=False)


class Summary(Base):
    """Episode summary and highlights."""
    
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False, unique=True)
    
    # Summary content
    executive_summary = Column(Text, nullable=False)
    key_points = Column(Text)  # JSON array of key points
    highlights = Column(Text)  # JSON array of highlights with timestamps
    topics = Column(Text)  # JSON array of topics discussed
    sentiment = Column(String(50))  # positive, negative, neutral
    
    # Metadata
    summary_length = Column(Integer)  # Number of words
    processing_time = Column(Float)  # Time taken to generate summary
    model_used = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    episode = relationship("Episode", back_populates="summary")


class ProcessingJob(Base):
    """Background processing job tracking."""
    
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True)
    job_type = Column(String(50), nullable=False)  # download, transcribe, summarize
    episode_id = Column(Integer, ForeignKey("episodes.id"))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    priority = Column(Integer, default=0)
    
    # Job metadata
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DigestLog(Base):
    """Daily digest delivery logs."""
    
    __tablename__ = "digest_logs"
    
    id = Column(Integer, primary_key=True)
    digest_date = Column(DateTime, nullable=False)
    episode_count = Column(Integer, default=0)
    
    # Delivery status
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime)
    email_error = Column(Text)
    
    slack_sent = Column(Boolean, default=False)
    slack_sent_at = Column(DateTime)
    slack_error = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow) 