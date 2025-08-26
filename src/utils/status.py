"""
Status utility for checking AI Podcast Agent health and statistics.
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from pathlib import Path

from ..core.config import settings
from ..database.models import Podcast, Episode, Summary, ProcessingJob


class SystemStatus:
    """System status and statistics checker."""
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        return self.SessionLocal()
    
    def check_system_health(self):
        """Check overall system health."""
        
        print("🏥 AI Podcast Agent - System Health Check")
        print("=" * 50)
        
        session = self.get_session()
        
        try:
            # Check database connection
            print("\n📊 Database Status:")
            podcast_count = session.query(Podcast).count()
            episode_count = session.query(Episode).count()
            summary_count = session.query(Summary).count()
            
            print(f"   Podcasts: {podcast_count}")
            print(f"   Episodes: {episode_count}")
            print(f"   Summaries: {summary_count}")
            
            # Check processing status
            print("\n⚙️  Processing Status:")
            downloaded = session.query(Episode).filter(Episode.downloaded == True).count()
            transcribed = session.query(Episode).filter(Episode.transcribed == True).count()
            summarized = session.query(Episode).filter(Episode.summarized == True).count()
            
            print(f"   Downloaded: {downloaded}/{episode_count} ({downloaded/episode_count*100:.1f}%)" if episode_count > 0 else "   Downloaded: 0/0 (0%)")
            print(f"   Transcribed: {transcribed}/{episode_count} ({transcribed/episode_count*100:.1f}%)" if episode_count > 0 else "   Transcribed: 0/0 (0%)")
            print(f"   Summarized: {summarized}/{episode_count} ({summarized/episode_count*100:.1f}%)" if episode_count > 0 else "   Summarized: 0/0 (0%)")
            
            # Check recent activity
            print("\n📅 Recent Activity:")
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)
            
            recent_episodes = session.query(Episode).filter(
                Episode.created_at >= week_ago
            ).count()
            
            print(f"   Episodes added this week: {recent_episodes}")
            
            # Check storage
            print("\n💾 Storage Status:")
            self._check_storage()
            
            # Check errors
            print("\n⚠️  Error Status:")
            error_episodes = session.query(Episode).filter(
                Episode.processing_error.isnot(None)
            ).count()
            
            if error_episodes > 0:
                print(f"   Episodes with errors: {error_episodes}")
                recent_errors = session.query(Episode).filter(
                    Episode.processing_error.isnot(None),
                    Episode.updated_at >= week_ago
                ).limit(3).all()
                
                for episode in recent_errors:
                    print(f"     - {episode.title}: {episode.processing_error[:50]}...")
            else:
                print("   No processing errors found")
            
            print("\n✅ System health check completed")
            
        except Exception as e:
            print(f"❌ Error checking system health: {e}")
        finally:
            session.close()
    
    def _check_storage(self):
        """Check storage directories and disk usage."""
        
        directories = [
            ("Audio", settings.audio_storage_path),
            ("Transcripts", settings.transcript_storage_path),
            ("Summaries", settings.summary_storage_path),
            ("Embeddings", settings.embedding_storage_path),
        ]
        
        for name, path in directories:
            if path.exists():
                try:
                    # Count files
                    file_count = len(list(path.rglob("*")))
                    print(f"   {name}: {file_count} files")
                except Exception as e:
                    print(f"   {name}: Error checking ({e})")
            else:
                print(f"   {name}: Directory not found")
    
    def show_recent_episodes(self, limit=5):
        """Show recent episodes."""
        
        print(f"\n📻 Recent Episodes (last {limit}):")
        print("-" * 50)
        
        session = self.get_session()
        
        try:
            episodes = session.query(Episode).order_by(
                Episode.created_at.desc()
            ).limit(limit).all()
            
            for episode in episodes:
                status = []
                if episode.downloaded:
                    status.append("📥")
                if episode.transcribed:
                    status.append("🎤")
                if episode.summarized:
                    status.append("📝")
                
                status_str = " ".join(status) if status else "⏳"
                
                print(f"{status_str} {episode.podcast.name}: {episode.title}")
                print(f"    Published: {episode.published_date.strftime('%Y-%m-%d')}")
                if episode.duration:
                    print(f"    Duration: {episode.duration // 60}m {episode.duration % 60}s")
                print()
                
        except Exception as e:
            print(f"Error fetching recent episodes: {e}")
        finally:
            session.close()


def main():
    """Main entry point for status check."""
    
    status = SystemStatus()
    status.check_system_health()
    status.show_recent_episodes()


if __name__ == "__main__":
    main() 