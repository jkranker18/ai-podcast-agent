"""
Test script for single episode transcription.
"""

import asyncio
import os

from src.core.config import Settings
from src.core.logger import setup_logging
from src.database.init_db import init_database, get_db_session
from src.workers.transcription_worker import TranscriptionWorker
from src.database.models import Episode


async def test_single_transcription():
    """Test transcription of a single episode."""
    print("🎯 Testing Single Episode Transcription")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    init_database()
    
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
    asyncio.run(test_single_transcription()) 