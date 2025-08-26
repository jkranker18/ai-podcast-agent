#!/usr/bin/env python3

from src.workers.transcription_worker import TranscriptionWorker
from src.workers.summarization_worker import SummarizationWorker
from src.core.config import Settings
from src.database.init_db import init_database, get_db_session
from src.database.models import Episode
from src.core.logger import setup_logging
from sqlalchemy import desc

def process_latest_episode():
    """Process only the most recent episode for transcription and summarization."""
    
    print("🎯 Processing Latest Episode Only")
    print("=" * 40)
    
    # Setup
    setup_logging()
    init_database()
    
    # Get the most recent episode
    with get_db_session() as session:
        latest_episode = session.query(Episode).filter(
            Episode.downloaded == True,
            Episode.transcript_file_path.is_(None)
        ).order_by(desc(Episode.published_date)).first()
        
        if not latest_episode:
            print("❌ No episodes found that need processing")
            return
        
        print(f"📋 Latest episode: {latest_episode.title}")
        print(f"🎙️  Podcast: {latest_episode.podcast.name}")
        print(f"📅 Published: {latest_episode.published_date}")
        print(f"⏱️  Duration: {latest_episode.transcript_duration or 'Unknown'} minutes")
        print()
        
        # Process transcription
        print("🎤 Starting transcription...")
        transcription_worker = TranscriptionWorker(Settings())
        transcription_success = transcription_worker.process_episode(latest_episode, session)
        
        if transcription_success:
            print("✅ Transcription completed successfully!")
            
            # Process summarization
            print("🧠 Starting summarization...")
            summarization_worker = SummarizationWorker(Settings())
            summarization_success = summarization_worker.process_episode(latest_episode, session)
            
            if summarization_success:
                print("✅ Summarization completed successfully!")
                print()
                print("🎉 Latest episode fully processed!")
                print(f"📄 Transcript: {latest_episode.transcript_file_path}")
                print(f"📝 Summary: {latest_episode.summary_file_path}")
            else:
                print("❌ Summarization failed")
        else:
            print("❌ Transcription failed")

if __name__ == "__main__":
    process_latest_episode() 