"""
Database initialization and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from src.core.config import Settings
from src.database.models import Base, Podcast
from contextlib import contextmanager


# Global session factory
SessionLocal = None


def get_database_url() -> str:
    """Get database URL from configuration."""
    config = Settings()
    return config.database_url


def create_database_engine():
    """Create database engine."""
    database_url = get_database_url()
    
    # Ensure the data directory exists
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    return create_engine(database_url, echo=False)


def get_session_factory():
    """Get or create session factory."""
    global SessionLocal
    
    if SessionLocal is None:
        engine = create_database_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal


@contextmanager
def get_db_session():
    """Get a database session with automatic cleanup."""
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def init_database():
    """Initialize the database with tables and initial data."""
    try:
        logger.info("Creating database tables...")
        
        # Create engine and tables
        engine = create_database_engine()
        Base.metadata.create_all(bind=engine)
        
        # Initialize session factory
        get_session_factory()
        
        # Check if podcasts already exist
        with get_db_session() as session:
            existing_podcasts = session.query(Podcast).count()
            
            if existing_podcasts == 0:
                logger.info("Adding initial podcast feeds...")
                _add_initial_podcasts(session)
            else:
                logger.info(f"Database already contains {existing_podcasts} podcasts")
        
        logger.info("Database initialization completed successfully")
        
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def _add_initial_podcasts(session: Session):
    """Add initial podcast feeds to the database."""
    
    # Podcast feed configurations
    PODCAST_FEEDS = [
        {
            "name": "AI Today Podcast",
            "rss_url": "https://feeds.buzzsprout.com/2502664.rss",
            "website_url": "https://www.pmi.org/ai-today-podcast",
            "description": "AI Today Podcast covers artificial intelligence, machine learning, and cognitive technologies.",
            "category": "AI/Technology"
        },
        {
            "name": "CEO AI Podcast", 
            "rss_url": "https://feeds.buzzsprout.com/2151922.rss",
            "website_url": "https://ceoai.com/",
            "description": "CEO AI Podcast explores how CEOs and business leaders are implementing AI in their organizations.",
            "category": "AI/Business"
        },
        {
            "name": "The TWIML AI Podcast",
            "rss_url": "https://twimlai.com/feed",
            "website_url": "https://twimlai.com/",
            "description": "The TWIML AI Podcast (formerly This Week in Machine Learning & Artificial Intelligence) features interviews with leading AI researchers and practitioners.",
            "category": "AI/Technology"
        },
        {
            "name": "Practical AI",
            "rss_url": "https://changelog.com/practicalai/feed",
            "website_url": "https://changelog.com/practicalai",
            "description": "Practical AI is a podcast about artificial intelligence in practice.",
            "category": "AI/Technology"
        },
        {
            "name": "Lex Fridman Podcast",
            "rss_url": "https://lexfridman.com/feed/podcast/",
            "website_url": "https://lexfridman.com/",
            "description": "The Lex Fridman Podcast features conversations about AI, science, technology, history, philosophy, and the nature of intelligence, consciousness, love, and power.",
            "category": "AI/Technology"
        }
    ]
    
    # Add podcasts to database
    for feed_config in PODCAST_FEEDS:
        podcast = Podcast(
            name=feed_config["name"],
            rss_url=feed_config["rss_url"],
            website_url=feed_config["website_url"],
            description=feed_config["description"],
            category=feed_config["category"]
        )
        session.add(podcast)
    
    session.commit()
    logger.info(f"Added {len(PODCAST_FEEDS)} podcast feeds to database") 