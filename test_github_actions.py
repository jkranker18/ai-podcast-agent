#!/usr/bin/env python3
"""
Minimal test script for GitHub Actions debugging.
"""

import os
import sys

def test_imports():
    """Test basic imports."""
    print("🔍 Testing imports...")
    try:
        import src
        print("✅ src module imported")
        
        from src.core.config import settings
        print("✅ config imported")
        
        from src.database.init_db import init_database
        print("✅ database init imported")
        
        from src.fetchers.rss_fetcher import RSSFetcher
        print("✅ RSS fetcher imported")
        
        from src.workers.transcription_worker import TranscriptionWorker
        print("✅ transcription worker imported")
        
        from src.workers.summarization_worker import SummarizationWorker
        print("✅ summarization worker imported")
        
        from src.workers.digest_composer import DigestComposer
        print("✅ digest composer imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    try:
        from src.core.config import settings
        print(f"✅ Email enabled: {settings.email_enabled}")
        print(f"✅ SMTP server: {settings.smtp_server}")
        print(f"✅ Subscriber emails: {settings.subscriber_emails}")
        return True
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\n🔍 Testing database...")
    try:
        from src.database.init_db import init_database
        init_database()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 GitHub Actions Debug Test")
    print("=" * 40)
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    print("✅ Logs directory created")
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    # Test config
    if not test_config():
        sys.exit(1)
    
    # Test database
    if not test_database():
        sys.exit(1)
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    main() 