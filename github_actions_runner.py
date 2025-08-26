#!/usr/bin/env python3
"""
GitHub Actions runner for AI Podcast Agent.
This script runs the complete pipeline for daily digest generation.
"""

import asyncio
import os
from src.core.logger import setup_logging
from src.database.init_db import init_database, get_db_session
from src.fetchers.rss_fetcher import RSSFetcher
from src.fetchers.audio_downloader import AudioDownloader
from src.workers.transcription_worker import TranscriptionWorker
from src.workers.summarization_worker import SummarizationWorker
from src.workers.digest_composer import DigestComposer

async def main():
    """Run the complete podcast processing pipeline."""
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Setup logging
    setup_logging()
    
    print("🚀 Starting AI Podcast Agent Pipeline")
    print("=" * 50)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Fetch new episodes
        print("📡 Fetching new episodes...")
        from src.core.config import settings
        fetcher = RSSFetcher(settings)
        await fetcher.fetch_podcast_feeds()
        print("✅ Episodes fetched")
        
        # Download audio files
        print("⬇️ Downloading audio files...")
        downloader = AudioDownloader(settings)
        await downloader.download_pending_episodes()
        print("✅ Audio files downloaded")
        
        # Transcribe episodes
        print("🎤 Transcribing episodes...")
        transcription_worker = TranscriptionWorker(settings)
        await transcription_worker.process_pending_episodes()
        print("✅ Episodes transcribed")
        
        # Generate summaries
        print("🧠 Generating summaries...")
        summarization_worker = SummarizationWorker(settings)
        await summarization_worker.process_pending_episodes()
        print("✅ Summaries generated")
        
        # Send email digest
        print("📧 Sending email digest...")
        composer = DigestComposer(settings)
        await composer.send_daily_digest()
        print("✅ Email digest sent")
        
        print("✅ Pipeline completed successfully!")
        
    except Exception as e:
        import traceback
        print(f"❌ Pipeline failed: {e}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 