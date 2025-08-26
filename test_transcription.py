"""
Test script for ASR transcription functionality.
"""

import asyncio
import os
from pathlib import Path

from src.core.config import Settings
from src.core.logger import setup_logging
from src.database.init_db import init_database
from src.workers.transcription_worker import TranscriptionWorker
from src.database.models import Episode
from src.database.init_db import get_db_session


async def test_transcription_setup():
    """Test the transcription worker setup."""
    print("🧪 Testing ASR Transcription Setup")
    print("=" * 50)
    
    # Initialize configuration and logging
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    print("1. Testing configuration...")
    print(f"   Whisper model: {config.whisper_model}")
    print(f"   Transcript storage: {config.transcript_storage_path}")
    print(f"   Max concurrent transcriptions: {config.max_concurrent_transcriptions}")
    print("   ✅ Configuration loaded successfully")
    
    # Initialize database
    print("\n2. Testing database...")
    init_database()
    print("   ✅ Database initialized successfully")
    
    # Test transcription worker
    print("\n3. Testing transcription worker...")
    worker = TranscriptionWorker(config)
    print("   ✅ Transcription worker created successfully")
    
    # Get transcription stats
    stats = worker.get_transcription_stats()
    print(f"   Total episodes with audio: {stats['total_episodes_with_audio']}")
    print(f"   Transcribed episodes: {stats['transcribed_episodes']}")
    print(f"   Pending transcription: {stats['pending_transcription']}")
    print(f"   Completion rate: {stats['completion_rate']:.1f}%")
    
    if stats['pending_transcription'] > 0:
        print(f"\n4. Testing transcription with {stats['pending_transcription']} episodes...")
        
        # Process pending episodes
        result = await worker.process_pending_episodes()
        print(f"   Processed: {result['processed']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")
        
        if result['successful'] > 0:
            print("   ✅ Transcription test completed successfully!")
        else:
            print("   ⚠️  No episodes were successfully transcribed")
    else:
        print("\n4. No episodes need transcription")
        print("   ✅ All episodes already transcribed")
    
    print("\n" + "=" * 50)
    print("🎉 Transcription setup test completed!")


async def test_single_episode_transcription():
    """Test transcription of a single episode."""
    print("\n🎯 Testing Single Episode Transcription")
    print("=" * 50)
    
    config = Settings()
    worker = TranscriptionWorker(config)
    
    with get_db_session() as db:
        # Get first episode with audio but no transcript
        episode = db.query(Episode).filter(
            Episode.audio_file_path.isnot(None),
            Episode.transcript_file_path.is_(None)
        ).first()
        
        if episode:
            print(f"Testing transcription of episode: {episode.title}")
            print(f"Audio file: {episode.audio_file_path}")
            
            # Check if audio file exists
            if os.path.exists(episode.audio_file_path):
                print("✅ Audio file exists")
                
                # Test transcription
                try:
                    result = worker.process_episode(episode, db)
                    if result:
                        print("✅ Episode transcribed successfully!")
                        
                        # Show transcript info
                        if episode.transcript_file_path:
                            print(f"Transcript saved to: {episode.transcript_file_path}")
                            print(f"Word count: {episode.transcript_word_count}")
                            print(f"Duration: {episode.transcript_duration:.1f} seconds")
                            print(f"Language: {episode.transcript_language}")
                    else:
                        print("❌ Episode transcription failed")
                except Exception as e:
                    print(f"❌ Transcription error: {e}")
            else:
                print("❌ Audio file not found")
        else:
            print("No episodes available for transcription testing")


if __name__ == "__main__":
    asyncio.run(test_transcription_setup())
    asyncio.run(test_single_episode_transcription()) 