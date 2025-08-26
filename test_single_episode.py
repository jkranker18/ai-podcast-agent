#!/usr/bin/env python3

import asyncio
from src.database.init_db import get_db_session
from src.database.models import Episode
from src.workers.transcription_worker import TranscriptionWorker
from src.workers.summarization_worker import SummarizationWorker
from src.core.config import Settings

async def test_single_episode():
    """Test processing a single episode to avoid hanging."""
    
    print("🎯 Testing Single Episode Processing")
    print("=" * 50)
    
    config = Settings()
    
    with get_db_session() as db:
        # Get one episode that needs transcription
        episode = db.query(Episode).filter(
            Episode.audio_file_path != None,
            Episode.transcript_file_path == None
        ).first()
        
        if not episode:
            print("❌ No episodes found that need transcription")
            return
        
        print(f"Processing episode: {episode.title}")
        print(f"Audio file: {episode.audio_file_path}")
        
        # Test transcription
        print("\n1. Testing transcription...")
        transcription_worker = TranscriptionWorker(config)
        success = transcription_worker.process_episode(episode, db)
        
        if success:
            print("✅ Transcription completed")
            
            # Test summarization
            print("\n2. Testing summarization...")
            summarization_worker = SummarizationWorker(config)
            summary_success = summarization_worker.process_episode(episode, db)
            
            if summary_success:
                print("✅ Summarization completed")
                print("🎉 Single episode processing successful!")
            else:
                print("❌ Summarization failed")
        else:
            print("❌ Transcription failed")

if __name__ == "__main__":
    asyncio.run(test_single_episode()) 