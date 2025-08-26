"""
Check transcription status in the database.
"""

from src.database.init_db import get_db_session
from src.database.models import Episode


def check_transcription_status():
    """Check which episodes have been transcribed."""
    with get_db_session() as session:
        # Get all episodes
        episodes = session.query(Episode).all()
        
        print("📊 Transcription Status:")
        print("=" * 50)
        
        transcribed_count = 0
        for episode in episodes:
            if episode.transcript_file_path:
                transcribed_count += 1
                print(f"✅ Episode {episode.id}: {episode.title[:50]}...")
                print(f"   Transcript: {episode.transcript_file_path}")
                print(f"   Word count: {episode.transcript_word_count}")
                print(f"   Duration: {episode.transcript_duration:.1f}s")
                print(f"   Language: {episode.transcript_language}")
                print()
        
        print(f"📈 Summary: {transcribed_count}/{len(episodes)} episodes transcribed")


if __name__ == "__main__":
    check_transcription_status() 