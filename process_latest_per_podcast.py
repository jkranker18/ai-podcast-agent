#!/usr/bin/env python3

from src.workers.transcription_worker import TranscriptionWorker
from src.workers.summarization_worker import SummarizationWorker
from src.core.config import Settings
from src.database.init_db import init_database, get_db_session
from src.database.models import Episode, Podcast
from src.core.logger import setup_logging
from sqlalchemy import desc
import time

def process_latest_per_podcast():
    """Process the latest episode from each podcast."""
    
    print("🎯 Processing Latest Episode from Each Podcast")
    print("=" * 50)
    
    # Setup
    setup_logging()
    init_database()
    
    # Get all podcasts
    with get_db_session() as session:
        podcasts = session.query(Podcast).filter(Podcast.active == True).all()
        
        print(f"📋 Found {len(podcasts)} active podcasts")
        print()
        
        # Get latest episode from each podcast
        latest_episodes = []
        for podcast in podcasts:
            latest = session.query(Episode).filter(
                Episode.podcast_id == podcast.id,
                Episode.downloaded == True,
                Episode.transcript_file_path.is_(None)
            ).order_by(desc(Episode.published_date)).first()
            
            if latest:
                latest_episodes.append(latest)
                print(f"🎙️  {podcast.name}: {latest.title[:60]}...")
            else:
                print(f"🎙️  {podcast.name}: No episodes to process")
        
        print()
        print(f"📊 Total episodes to process: {len(latest_episodes)}")
        
        if not latest_episodes:
            print("❌ No episodes found that need processing")
            return
        
        # Estimate processing time
        # Based on previous experience: ~1 hour per episode for transcription + ~15 min for summarization
        estimated_hours = len(latest_episodes) * 1.25
        print(f"⏱️  Estimated processing time: {estimated_hours:.1f} hours")
        print()
        
        # Ask for confirmation
        response = input("Continue with processing? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Processing cancelled")
            return
        
        # Process each episode
        transcription_worker = TranscriptionWorker(Settings())
        summarization_worker = SummarizationWorker(Settings())
        
        for i, episode in enumerate(latest_episodes, 1):
            print(f"\n🎯 Processing episode {i}/{len(latest_episodes)}")
            print(f"📋 {episode.podcast.name}: {episode.title}")
            print(f"📅 Published: {episode.published_date}")
            
            start_time = time.time()
            
            # Process transcription
            print("🎤 Starting transcription...")
            transcription_success = transcription_worker.process_episode(episode, session)
            
            if transcription_success:
                print("✅ Transcription completed!")
                
                # Process summarization
                print("🧠 Starting summarization...")
                summarization_success = summarization_worker.process_episode(episode, session)
                
                if summarization_success:
                    elapsed_time = time.time() - start_time
                    print(f"✅ Summarization completed! (Total time: {elapsed_time/60:.1f} minutes)")
                else:
                    print("❌ Summarization failed")
            else:
                print("❌ Transcription failed")
        
        print(f"\n🎉 Processing complete! {len(latest_episodes)} episodes processed.")

if __name__ == "__main__":
    process_latest_per_podcast() 