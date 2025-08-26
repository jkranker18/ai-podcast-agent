"""
Test script to preview email digest using existing summary file.
"""

import asyncio
import os
import json
from datetime import datetime

from src.core.config import Settings
from src.core.logger import setup_logging
from src.workers.digest_composer import DigestComposer


async def test_digest_preview():
    """Test email digest preview using existing summary file."""
    print("📧 Testing Email Digest Preview")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    composer = DigestComposer(config)
    
    # Check if we have our test summary
    summary_file = "data/summaries/episode_999_summary.json"
    
    if os.path.exists(summary_file):
        print(f"✅ Found test summary: {summary_file}")
        
        # Load the summary data
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_data = json.load(f)
        
        print(f"   Summary data loaded: {len(summary_data)} fields")
        
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
        
        print(f"\n1. Testing HTML digest generation...")
        try:
            html_content = composer._create_digest_html(episodes, datetime.utcnow())
            print(f"   ✅ HTML digest generated ({len(html_content)} characters)")
            
            # Save HTML digest for preview
            with open("test_digest.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("   💾 HTML digest saved to test_digest.html")
            
            # Show a preview
            print(f"   📋 Preview: {html_content[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error generating HTML digest: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n2. Testing text digest generation...")
        try:
            text_content = composer._create_digest_text(episodes, datetime.utcnow())
            print(f"   ✅ Text digest generated ({len(text_content)} characters)")
            
            # Save text digest for preview
            with open("test_digest.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
            print("   💾 Text digest saved to test_digest.txt")
            
            # Show a preview
            print(f"   📋 Preview: {text_content[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error generating text digest: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\n3. Email configuration status:")
        print(f"   Email enabled: {config.email_enabled}")
        print(f"   SMTP server: {config.smtp_server}:{config.smtp_port}")
        print(f"   From: {config.email_user}")
        print(f"   To: {config.recipient_email}")
        
        if not config.email_enabled:
            print(f"\n   ⚠️  Email is disabled. To enable:")
            print(f"   - Set EMAIL_ENABLED=true in .env")
            print(f"   - Configure SMTP settings (EMAIL_USER, EMAIL_PASSWORD, etc.)")
        
    else:
        print(f"❌ Test summary file not found: {summary_file}")
        print("   Run the summarization test first to generate a summary")
    
    print("\n" + "=" * 50)
    print("🎉 Email digest preview test completed!")


if __name__ == "__main__":
    asyncio.run(test_digest_preview()) 