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
    
    # Setup logging
    setup_logging()
    
    print("🚀 Starting AI Podcast Agent Pipeline")
    print("=" * 50)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        init_database()
        
        # Fetch new episodes
        print("📡 Fetching new episodes...")
        fetcher = RSSFetcher()
        await fetcher.fetch_podcast_feeds()
        
        # Download audio files
        print("⬇️ Downloading audio files...")
        downloader = AudioDownloader()
        await downloader.download_pending_episodes()
        
        # Transcribe episodes
        print("🎤 Transcribing episodes...")
        transcription_worker = TranscriptionWorker()
        await transcription_worker.process_pending_episodes()
        
        # Generate summaries
        print("🧠 Generating summaries...")
        summarization_worker = SummarizationWorker()
        await summarization_worker.process_pending_episodes()
        
        # Send email digest
        print("📧 Sending email digest...")
        composer = DigestComposer()
        await composer.send_daily_digest()
        
        print("✅ Pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 