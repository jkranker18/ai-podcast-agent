"""
Test script to verify the AI Podcast Agent setup.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config import settings
from src.core.logger import setup_logging
from src.database.init_db import init_database
from loguru import logger


async def test_basic_setup():
    """Test basic setup and configuration."""
    
    print("🧪 Testing AI Podcast Agent Setup")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing configuration...")
    try:
        print(f"   Database URL: {settings.database_url}")
        print(f"   Audio storage: {settings.audio_storage_path}")
        print(f"   Transcript storage: {settings.transcript_storage_path}")
        print(f"   Summary storage: {settings.summary_storage_path}")
        print("   ✅ Configuration loaded successfully")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Database initialization
    print("\n2. Testing database initialization...")
    try:
        init_database()
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Database initialization error: {e}")
        return False
    
    # Test 3: Directory creation
    print("\n3. Testing directory creation...")
    try:
        directories = [
            settings.audio_storage_path,
            settings.transcript_storage_path,
            settings.summary_storage_path,
            settings.embedding_storage_path,
            "logs"
        ]
        
        for directory in directories:
            if Path(directory).exists():
                print(f"   ✅ Directory exists: {directory}")
            else:
                print(f"   ❌ Directory missing: {directory}")
                return False
    except Exception as e:
        print(f"   ❌ Directory test error: {e}")
        return False
    
    # Test 4: Import tests
    print("\n4. Testing imports...")
    try:
        from src.fetchers.rss_fetcher import RSSFetcher
        from src.fetchers.audio_downloader import AudioDownloader
        from src.database.models import Podcast, Episode, Summary
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    print("\n🎉 All tests passed! The AI Podcast Agent is ready to use.")
    return True


async def test_rss_fetch():
    """Test RSS feed fetching."""
    
    print("\n📡 Testing RSS Feed Fetching")
    print("=" * 50)
    
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.fetchers.rss_fetcher import RSSFetcher
        
        # Create database session
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        # Test RSS fetcher
        fetcher = RSSFetcher(session)
        episodes = fetcher.fetch_podcast_feeds()
        
        print(f"   Found {len(episodes)} new episodes")
        
        if episodes:
            # Save a few episodes for testing
            saved_episodes = fetcher.save_episodes(episodes[:1])  # Save first 1
            print(f"   Saved {len(saved_episodes)} episodes to database")
        
        session.close()
        print("   ✅ RSS fetching test completed")
        return True
        
    except Exception as e:
        print(f"   ❌ RSS fetching error: {e}")
        return False


def main():
    """Run all tests."""
    
    # Setup logging
    setup_logging()
    
    # Run tests
    success = asyncio.run(test_basic_setup())
    
    if success:
        asyncio.run(test_rss_fetch())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup verification completed successfully!")
        print("\nNext steps:")
        print("1. Copy env.example to .env and configure your settings")
        print("2. Run: python -m src.main")
        print("3. Or run with scheduler: python -m src.main --scheduler")
    else:
        print("❌ Setup verification failed. Please check the errors above.")


if __name__ == "__main__":
    main() 