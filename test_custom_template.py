#!/usr/bin/env python3

import asyncio
from datetime import datetime
from pathlib import Path
from src.workers.digest_composer import DigestComposer
from src.core.config import Settings
from src.database.init_db import init_database, get_db_session
from src.database.models import Episode, Podcast
from src.core.logger import setup_logging

def test_custom_template():
    """Test the custom email template with real data."""
    
    print("🎨 Testing Custom Email Template")
    print("=" * 40)
    
    # Setup
    setup_logging()
    init_database()
    
    # Create composer
    config = Settings()
    composer = DigestComposer(config)
    
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
    
    # Test HTML generation
    print("🔧 Generating HTML with custom template...")
    html_content = composer._create_digest_html(episodes, datetime.utcnow())
    
    if html_content:
        print("✅ HTML generated successfully!")
        
        # Save preview
        preview_file = "email_preview.html"
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📄 Preview saved to: {preview_file}")
        
        # Test email sending
        print("\n📤 Testing email sending...")
        success = composer.send_digest(episodes)
        
        if success:
            print("✅ Test email sent successfully!")
            print(f"📧 Sent to: {config.recipient_email}")
        else:
            print("❌ Failed to send test email")
    else:
        print("❌ Failed to generate HTML content")

if __name__ == "__main__":
    test_custom_template() 