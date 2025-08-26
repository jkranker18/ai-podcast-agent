#!/usr/bin/env python3

from src.workers.digest_composer import DigestComposer
from src.core.config import Settings
from src.database.init_db import init_database, get_db_session
from src.database.models import Episode, Podcast
from src.core.logger import setup_logging
from datetime import datetime
from pathlib import Path

def test_multiple_subscribers():
    """Test sending email to multiple subscribers."""
    
    print("📧 Testing Multiple Subscribers")
    print("=" * 40)
    
    # Setup
    setup_logging()
    init_database()
    
    # Create composer
    config = Settings()
    composer = DigestComposer(config)
    
    # Show current subscribers
    subscribers = composer._get_subscriber_list()
    print(f"📋 Current subscribers ({len(subscribers)}):")
    for email in subscribers:
        print(f"  • {email}")
    print()
    
    if not subscribers:
        print("❌ No subscribers configured!")
        print("Please run add_subscriber.py to add subscribers first.")
        return
    
    # Check if we have any existing summaries
    summary_files = list(Path("data/summaries").glob("*.json"))
    
    if not summary_files:
        print("❌ No summary files found!")
        print("Please run the full pipeline first to generate some summaries.")
        return
    
    print(f"📋 Found {len(summary_files)} summary files")
    
    # Create a mock episode for testing
    with get_db_session() as session:
        # Get the first podcast
        podcast = session.query(Podcast).first()
        if not podcast:
            print("❌ No podcasts found in database!")
            return
        
        # Create a mock episode with the existing summary
        mock_episode = Episode(
            id=999,
            title="Test Episode - AI in Healthcare",
            podcast=podcast,
            published_date=datetime.utcnow(),
            transcript_duration=1800,  # 30 minutes
            transcript_word_count=4814,
            summary_file_path=str(summary_files[0])
        )
        
        episodes = [mock_episode]
    
    print(f"📧 Testing with {len(episodes)} mock episode(s)")
    print(f"📊 Total words: {sum(ep.transcript_word_count or 0 for ep in episodes):,}")
    print(f"⏱️  Total duration: {sum(ep.transcript_duration or 0 for ep in episodes)/60:.1f} minutes")
    print()
    
    # Test email sending to all subscribers
    print("📤 Testing email sending to all subscribers...")
    success = composer.send_digest(episodes)
    
    if success:
        print("✅ Test email sent successfully to all subscribers!")
        print(f"📧 Sent to {len(subscribers)} subscriber(s)")
    else:
        print("❌ Failed to send test email")
    
    print()
    print("💡 Note: Each subscriber will receive their own individual email")

if __name__ == "__main__":
    test_multiple_subscribers() 