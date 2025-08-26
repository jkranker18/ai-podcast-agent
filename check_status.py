#!/usr/bin/env python3

from src.database.init_db import get_db_session
from src.database.models import Episode, Podcast

def main():
    print("📊 Database Status Check")
    print("=" * 50)
    
    with get_db_session() as db:
        # Check total episodes
        total_episodes = db.query(Episode).count()
        print(f"Total episodes: {total_episodes}")
        
        if total_episodes > 0:
            # Check processing status
            pending_download = db.query(Episode).filter(Episode.audio_file_path == None).count()
            pending_transcription = db.query(Episode).filter(
                Episode.audio_file_path != None, 
                Episode.transcript_file_path == None
            ).count()
            pending_summary = db.query(Episode).filter(
                Episode.transcript_file_path != None, 
                Episode.summary_file_path == None
            ).count()
            
            print(f"Pending download: {pending_download}")
            print(f"Pending transcription: {pending_transcription}")
            print(f"Pending summary: {pending_summary}")
            
            # Show recent episodes
            recent_episodes = db.query(Episode).order_by(Episode.published_date.desc()).limit(5).all()
            print(f"\nRecent {len(recent_episodes)} episodes:")
            for episode in recent_episodes:
                podcast = db.query(Podcast).filter(Podcast.id == episode.podcast_id).first()
                status = []
                if episode.audio_file_path:
                    status.append("✅ Downloaded")
                else:
                    status.append("⏳ Download pending")
                    
                if episode.transcript_file_path:
                    status.append("✅ Transcribed")
                elif episode.audio_file_path:
                    status.append("⏳ Transcription pending")
                    
                if episode.summary_file_path:
                    status.append("✅ Summarized")
                elif episode.transcript_file_path:
                    status.append("⏳ Summary pending")
                
                print(f"  • {podcast.name}: {episode.title[:50]}...")
                print(f"    Status: {' | '.join(status)}")
                print(f"    Published: {episode.published_date}")
                print()
        
        # Check podcasts
        podcasts = db.query(Podcast).all()
        print(f"Configured podcasts: {len(podcasts)}")
        for podcast in podcasts:
            episode_count = db.query(Episode).filter(Episode.podcast_id == podcast.id).count()
            print(f"  • {podcast.name}: {episode_count} episodes")

if __name__ == "__main__":
    main() 