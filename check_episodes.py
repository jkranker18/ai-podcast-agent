#!/usr/bin/env python3

from src.database.init_db import get_db_session
from src.database.models import Episode
from src.core.logger import setup_logging

def main():
    """Check episodes with transcripts and summaries."""
    
    setup_logging()
    
    with get_db_session() as session:
        # Check episodes with transcripts
        episodes_with_transcripts = session.query(Episode).filter(
            Episode.transcript_file_path.isnot(None)
        ).all()
        
        print(f"📝 Episodes with transcripts: {len(episodes_with_transcripts)}")
        
        # Check episodes with summaries
        episodes_with_summaries = session.query(Episode).filter(
            Episode.summary_file_path.isnot(None)
        ).all()
        
        print(f"📋 Episodes with summaries: {len(episodes_with_summaries)}")
        
        # Show first few episodes with summaries
        if episodes_with_summaries:
            print("\n📧 Episodes with summaries:")
            for ep in episodes_with_summaries[:3]:
                print(f"  • {ep.podcast.name}: {ep.title[:60]}...")
                print(f"    Transcript: {ep.transcript_file_path}")
                print(f"    Summary: {ep.summary_file_path}")
                print()

if __name__ == "__main__":
    main() 