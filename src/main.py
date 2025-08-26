"""
Main application entry point for the AI Podcast Agent.
"""

import asyncio
import argparse
import schedule
import time
from loguru import logger

from src.core.config import Settings
from src.core.logger import setup_logging
from src.database.init_db import init_database
from src.fetchers.rss_fetcher import RSSFetcher
from src.fetchers.audio_downloader import AudioDownloader
from src.workers.transcription_worker import TranscriptionWorker
from src.workers.summarization_worker import SummarizationWorker
from src.workers.digest_composer import DigestComposer


class PodcastAgent:
    """Main agent class that orchestrates the podcast processing pipeline."""
    
    def __init__(self):
        self.config = Settings()
        setup_logging(self.config.log_level, self.config.log_file)
        logger.info("AI Podcast Agent initialized")
        
        # Initialize components
        self.rss_fetcher = RSSFetcher(self.config)
        self.audio_downloader = AudioDownloader(self.config)
        self.transcription_worker = TranscriptionWorker(self.config)
        self.summarization_worker = SummarizationWorker(self.config)
        self.digest_composer = DigestComposer(self.config)
    
    async def fetch_new_episodes(self) -> int:
        """Fetch new episodes from RSS feeds."""
        logger.info("Fetching new episodes from RSS feeds...")
        
        episodes = await self.rss_fetcher.fetch_podcast_feeds()
        logger.info(f"Fetched and saved {len(episodes)} new episodes")
        return len(episodes)
    
    async def download_pending_episodes(self) -> dict:
        """Download audio files for pending episodes."""
        logger.info("Starting audio downloads...")
        
        stats = await self.audio_downloader.download_pending_episodes()
        logger.info(f"Download completed: {stats['downloaded']} successful, {stats['failed']} failed")
        return stats
    
    async def transcribe_pending_episodes(self) -> dict:
        """Transcribe audio files for pending episodes."""
        logger.info("Starting transcription of pending episodes...")
        
        stats = await self.transcription_worker.process_pending_episodes()
        logger.info(f"Transcription completed: {stats['successful']} successful, {stats['failed']} failed")
        return stats
    
    async def summarize_pending_episodes(self) -> dict:
        """Summarize transcripts for pending episodes."""
        logger.info("Starting summarization of pending episodes...")
        
        stats = await self.summarization_worker.process_pending_episodes()
        logger.info(f"Summarization completed: {stats['successful']} successful, {stats['failed']} failed")
        return stats
    
    async def run_pipeline(self) -> dict:
        """Run the complete podcast processing pipeline."""
        logger.info("Starting podcast processing pipeline...")
        
        # Step 1: Fetch new episodes
        new_episodes = await self.fetch_new_episodes()
        
        # Step 2: Download audio files
        download_stats = await self.download_pending_episodes()
        
        # Step 3: Transcribe audio files
        transcription_stats = await self.transcribe_pending_episodes()
        
        # Step 4: Summarize transcripts
        summarization_stats = await self.summarize_pending_episodes()
        
        # Summary
        pipeline_stats = {
            "new_episodes": new_episodes,
            "downloads": download_stats,
            "transcriptions": transcription_stats,
            "summarizations": summarization_stats
        }
        
        logger.info(f"Pipeline completed: {pipeline_stats}")
        return pipeline_stats
    
    def schedule_jobs(self):
        """Schedule recurring jobs."""
        # Check for new episodes every 6 hours
        schedule.every(self.config.feed_check_interval_hours).hours.do(
            lambda: asyncio.run(self.run_pipeline())
        )
        
        # Send daily digest at 8 AM
        schedule.every().day.at(self.config.digest_send_time).do(
            lambda: asyncio.run(self.send_daily_digest())
        )
        
        logger.info(f"Scheduled jobs: RSS check every {self.config.feed_check_interval_hours} hours, digest at {self.config.digest_send_time}")
    
    async def send_daily_digest(self):
        """Send daily digest."""
        logger.info("Sending daily digest...")
        
        # Use the digest composer to send the daily digest
        success = self.digest_composer.send_daily_digest()
        
        if success:
            logger.info("Daily digest sent successfully")
        else:
            logger.error("Failed to send daily digest")
        
        return success
    
    def run_scheduler(self):
        """Run the scheduled jobs."""
        self.schedule_jobs()
        
        logger.info("Starting scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def run_once(self):
        """Run the pipeline once."""
        return await self.run_pipeline()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI Podcast Agent")
    parser.add_argument("--scheduler", action="store_true", help="Run in scheduler mode")
    args = parser.parse_args()
    
    # Initialize database
    init_database()
    
    # Create agent
    agent = PodcastAgent()
    
    if args.scheduler:
        agent.run_scheduler()
    else:
        await agent.run_once()


if __name__ == "__main__":
    asyncio.run(main()) 