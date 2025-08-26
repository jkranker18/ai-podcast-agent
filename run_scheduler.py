#!/usr/bin/env python3

import asyncio
import schedule
import time
from src.main import PodcastAgent
from src.database.init_db import init_database
from src.core.logger import setup_logging

def main():
    """Run the scheduler with 6:00 AM digest time."""
    
    print("🤖 Starting AI Podcast Agent Scheduler")
    print("=" * 50)
    print("📅 Daily digest will be sent at 6:00 AM")
    print("📡 RSS feeds will be checked every 6 hours")
    print("📧 Email will be sent to: jkranker@gmail.com")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Initialize database
    init_database()
    
    # Create agent
    agent = PodcastAgent()
    
    # Override the digest time to 6:00 AM
    agent.config.digest_send_time = "06:00"
    
    # Schedule jobs
    agent.schedule_jobs()
    
    print("✅ Scheduler started successfully!")
    print("🔄 Running in background... Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main() 