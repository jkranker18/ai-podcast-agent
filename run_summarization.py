#!/usr/bin/env python3

import asyncio
from src.workers.summarization_worker import SummarizationWorker
from src.core.config import Settings
from src.core.logger import setup_logging
from src.database.init_db import init_database

async def main():
    """Run summarization worker to process all pending episodes."""
    
    print("🧠 Running Summarization Worker")
    print("=" * 40)
    
    # Setup
    setup_logging()
    init_database()
    
    # Create worker
    config = Settings()
    worker = SummarizationWorker(config)
    
    # Process pending episodes
    print("🔍 Processing pending episodes...")
    await worker.process_pending_episodes()
    
    print("✅ Summarization complete!")

if __name__ == "__main__":
    asyncio.run(main()) 