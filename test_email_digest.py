"""
Test script for email digest functionality.
"""

import asyncio
import os

from src.core.config import Settings
from src.core.logger import setup_logging
from src.workers.digest_composer import DigestComposer


async def test_email_digest():
    """Test email digest generation and sending."""
    print("📧 Testing Email Digest System")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    composer = DigestComposer(config)
    
    print("1. Testing digest composition...")
    
    # Get recent episodes
    episodes = composer.get_recent_episodes(days=7)  # Get episodes from last 7 days
    print(f"   Found {len(episodes)} episodes with summaries")
    
    if episodes:
        for episode in episodes:
            print(f"   - {episode.title} ({episode.podcast.name})")
        
        print("\n2. Testing HTML digest generation...")
        try:
            html_content = composer._create_digest_html(episodes, config.digest_send_time)
            print(f"   ✅ HTML digest generated ({len(html_content)} characters)")
            
            # Save HTML digest for preview
            with open("test_digest.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("   💾 HTML digest saved to test_digest.html")
            
        except Exception as e:
            print(f"   ❌ Error generating HTML digest: {e}")
        
        print("\n3. Testing text digest generation...")
        try:
            text_content = composer._create_digest_text(episodes, config.digest_send_time)
            print(f"   ✅ Text digest generated ({len(text_content)} characters)")
            
            # Save text digest for preview
            with open("test_digest.txt", "w", encoding="utf-8") as f:
                f.write(text_content)
            print("   💾 Text digest saved to test_digest.txt")
            
        except Exception as e:
            print(f"   ❌ Error generating text digest: {e}")
        
        print("\n4. Testing email configuration...")
        print(f"   Email enabled: {config.email_enabled}")
        print(f"   SMTP server: {config.smtp_server}:{config.smtp_port}")
        print(f"   From: {config.email_user}")
        print(f"   To: {config.recipient_email}")
        
        if config.email_enabled and config.email_user and config.recipient_email:
            print("\n5. Testing email sending...")
            try:
                success = composer.send_digest(episodes)
                if success:
                    print("   ✅ Email digest sent successfully!")
                else:
                    print("   ❌ Failed to send email digest")
            except Exception as e:
                print(f"   ❌ Error sending email: {e}")
        else:
            print("   ⚠️  Email not configured - skipping send test")
            print("   To enable email, set EMAIL_ENABLED=true and configure SMTP settings in .env")
    
    else:
        print("   ⚠️  No episodes with summaries found")
        print("   Run transcription and summarization first to generate content")
    
    print("\n" + "=" * 50)
    print("🎉 Email digest test completed!")


if __name__ == "__main__":
    asyncio.run(test_email_digest()) 