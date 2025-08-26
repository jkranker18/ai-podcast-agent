"""
RSS feed fetcher for podcast episodes.
"""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urlparse
from loguru import logger

from src.database.models import Podcast, Episode
from src.database.init_db import get_db_session
from src.core.config import Settings


class RSSFetcher:
    """Fetches and parses RSS feeds for podcast episodes."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.headers = {
            'User-Agent': 'AI-Podcast-Agent/1.0 (https://github.com/your-repo)'
        }
    
    async def fetch_podcast_feeds(self) -> List[Dict]:
        """Fetch all active podcast feeds and return new episodes."""
        
        logger.info("Fetching podcast feeds...")
        new_episodes = []
        
        with get_db_session() as session:
            # Get all active podcasts
            podcasts = session.query(Podcast).filter(Podcast.active == True).all()
            
            for podcast in podcasts:
                try:
                    episodes = self._fetch_feed(podcast, session)
                    new_episodes.extend(episodes)
                    logger.info(f"Found {len(episodes)} new episodes from {podcast.name}")
                    
                except Exception as e:
                    logger.error(f"Error fetching feed for {podcast.name}: {e}")
                    continue
            
            # Save episodes to database
            if new_episodes:
                saved_episodes = self.save_episodes(new_episodes, session)
                logger.info(f"Saved {len(saved_episodes)} new episodes to database")
                return saved_episodes
        
        return []
    
    def _fetch_feed(self, podcast: Podcast, session) -> List[Dict]:
        """Fetch and parse a single podcast feed."""
        
        try:
            # Fetch RSS feed
            response = requests.get(podcast.rss_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warning for {podcast.name}: {feed.bozo_exception}")
            
            episodes = []
            
            # Only process the last 10 episodes to avoid overwhelming the system
            recent_entries = feed.entries[:10]
            
            for entry in recent_entries:
                try:
                    episode_data = self._parse_episode_entry(entry, podcast.id, session)
                    if episode_data:
                        episodes.append(episode_data)
                        
                except Exception as e:
                    logger.error(f"Error parsing episode from {podcast.name}: {e}")
                    continue
            
            return episodes
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching {podcast.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching {podcast.name}: {e}")
            raise
    
    def _parse_episode_entry(self, entry, podcast_id: int, session) -> Optional[Dict]:
        """Parse a single episode entry from RSS feed."""
        
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            description = entry.get('summary', '').strip()
            published_date = self._parse_date(entry.get('published', ''))
            guid = entry.get('id', entry.get('link', ''))
            
            # Extract audio URL
            audio_url = self._extract_audio_url(entry)
            if not audio_url:
                logger.warning(f"No audio URL found for episode: {title}")
                return None
            
            # Extract additional metadata
            duration = self._parse_duration(entry)
            file_size = self._parse_file_size(entry)
            episode_url = entry.get('link', '')
            
            # Check if episode already exists
            existing_episode = session.query(Episode).filter(
                Episode.guid == guid
            ).first()
            
            if existing_episode:
                return None  # Episode already exists
            
            return {
                'podcast_id': podcast_id,
                'title': title,
                'description': description,
                'published_date': published_date,
                'duration': duration,
                'audio_url': audio_url,
                'episode_url': episode_url,
                'guid': guid,
                'file_size': file_size
            }
            
        except Exception as e:
            logger.error(f"Error parsing episode entry: {e}")
            return None
    
    def _extract_audio_url(self, entry) -> Optional[str]:
        """Extract audio URL from RSS entry."""
        
        # Check enclosures first
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('audio/'):
                    return enclosure.get('href', '')
        
        # Check media content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('type', '').startswith('audio/'):
                    return media.get('url', '')
        
        # Check links
        if hasattr(entry, 'links') and entry.links:
            for link in entry.links:
                if link.get('type', '').startswith('audio/'):
                    return link.get('href', '')
        
        return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        
        if not date_str:
            return datetime.utcnow()
        
        try:
            # Try parsing with feedparser's date parser
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                return datetime(*parsed_date[:6])
        except:
            pass
        
        # Fallback to current time
        return datetime.utcnow()
    
    def _parse_duration(self, entry) -> Optional[int]:
        """Parse duration from RSS entry."""
        
        # Check itunes duration
        if hasattr(entry, 'itunes_duration'):
            duration_str = entry.itunes_duration
            try:
                return self._parse_duration_string(duration_str)
            except:
                pass
        
        # Check media duration
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                duration = media.get('duration')
                if duration:
                    try:
                        return int(duration)
                    except:
                        pass
        
        return None
    
    def _parse_duration_string(self, duration_str: str) -> int:
        """Parse duration string (e.g., '1:30:45') to seconds."""
        
        if not duration_str:
            return 0
        
        parts = duration_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        else:
            return 0
    
    def _parse_file_size(self, entry) -> Optional[int]:
        """Parse file size from RSS entry."""
        
        # Check enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enclosure in entry.enclosures:
                length = enclosure.get('length')
                if length:
                    try:
                        return int(length)
                    except:
                        pass
        
        return None
    
    def save_episodes(self, episodes: List[Dict], session) -> List[Episode]:
        """Save new episodes to database."""
        
        saved_episodes = []
        
        for episode_data in episodes:
            try:
                episode = Episode(**episode_data)
                session.add(episode)
                saved_episodes.append(episode)
                
            except Exception as e:
                logger.error(f"Error saving episode {episode_data.get('title', 'Unknown')}: {e}")
                continue
        
        try:
            session.commit()
            logger.info(f"Saved {len(saved_episodes)} new episodes to database")
        except Exception as e:
            logger.error(f"Error committing episodes to database: {e}")
            session.rollback()
            return []
        
        return saved_episodes 