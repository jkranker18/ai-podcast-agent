"""
Test script to send an email using the configured settings.
"""

import asyncio
import os
import json
from datetime import datetime

from src.core.config import Settings
from src.core.logger import setup_logging
from src.workers.digest_composer import DigestComposer


async def test_send_email():
    """Test sending an email with our existing summary."""
    print("📧 Testing Email Sending")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    print(f"Email enabled: {config.email_enabled}")
    print(f"SMTP server: {config.smtp_server}:{config.smtp_port}")
    print(f"From: {config.email_user}")
    print(f"To: {config.recipient_email}")
    
    if not config.email_enabled:
        print("❌ Email is disabled in configuration")
        return
    
    composer = DigestComposer(config)
    
    # Check if we have our test summary
    summary_file = "data/summaries/episode_999_summary.json"
    
    if os.path.exists(summary_file):
        print(f"✅ Found test summary: {summary_file}")
        
        # Load the summary data
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        # Create a mock episode for testing
        class MockEpisode:
            def __init__(self):
                self.id = 999
                self.title = "Dr. Lukasz Kowalczyk on Practical AI Adoption in Healthcare"
                self.published_date = datetime.utcnow()
                self.transcript_duration = 1808.4
                self.transcript_word_count = 4814
                self.summary_file_path = summary_file
                
                class MockPodcast:
                    def __init__(self):
                        self.name = "AI Today Podcast"
                
                self.podcast = MockPodcast()
        
        mock_episode = MockEpisode()
        episodes = [mock_episode]
        
        print(f"\n📤 Sending test email...")
        try:
            success = composer.send_digest(episodes)
            if success:
                print("✅ Email sent successfully!")
                print("📧 Check your inbox for the AI Podcast Digest")
            else:
                print("❌ Failed to send email")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print(f"❌ Test summary file not found: {summary_file}")


if __name__ == "__main__":
    asyncio.run(test_send_email()) 