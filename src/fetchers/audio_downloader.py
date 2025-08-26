"""
Audio downloader for podcast episodes.
"""

import asyncio
import aiohttp
import os
import yt_dlp
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urlparse
from loguru import logger

from src.database.models import Episode
from src.database.init_db import get_db_session
from src.core.config import Settings


class AudioDownloader:
    """Downloads audio files for podcast episodes."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_downloads)
    
    async def download_pending_episodes(self) -> Dict:
        """Download audio files for all pending episodes."""
        
        logger.info("Starting audio downloads...")
        
        with get_db_session() as session:
            # Get episodes that need downloading
            episodes = session.query(Episode).filter(
                Episode.audio_file_path.is_(None),
                Episode.downloaded == False
            ).all()
            
            if not episodes:
                logger.info("No episodes need downloading")
                return {"downloaded": 0, "failed": 0}
            
            logger.info(f"Found {len(episodes)} episodes to download")
            
            # Download episodes in parallel
            tasks = []
            for episode in episodes:
                task = asyncio.create_task(
                    self._download_episode_with_semaphore(episode, session)
                )
                tasks.append(task)
            
            # Wait for all downloads to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            failed = len(results) - successful
            
            logger.info(f"Download completed: {successful} successful, {failed} failed")
            
            return {
                "downloaded": successful,
                "failed": failed
            } 
    
    async def _download_episode_with_semaphore(self, episode: Episode, session) -> bool:
        """Download episode with semaphore control."""
        async with self.semaphore:
            return await self._download_episode(episode, session)
    
    async def _download_episode(self, episode: Episode, session) -> bool:
        """Download audio file for a single episode."""
        
        try:
            logger.info(f"Starting download for episode: {episode.title}")
            
            # Determine file path
            file_path = self._get_audio_file_path(episode)
            
            # Create directory if it doesn't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            success = await self._download_file(episode.audio_url, file_path)
            
            if success:
                # Update episode with file path and completion status
                episode.audio_file_path = str(file_path)
                episode.downloaded = True
                episode.processing_error = None
                
                logger.info(f"Successfully downloaded: {episode.title}")
                return True
            else:
                # Update error status
                episode.processing_error = "Download failed"
                episode.retry_count += 1
                
                logger.error(f"Failed to download: {episode.title}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading episode {episode.title}: {e}")
            
            # Update error status
            episode.processing_error = str(e)
            episode.retry_count += 1
            
            return False
    
    async def _download_file(self, url: str, file_path: Path) -> bool:
        """Download file from URL to local path."""
        
        # Check if URL is YouTube
        if self._is_youtube_url(url):
            return await self._download_youtube(url, file_path)
        else:
            return await self._download_direct(url, file_path)
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is a YouTube video."""
        
        youtube_domains = [
            'youtube.com',
            'youtu.be',
            'www.youtube.com',
            'm.youtube.com'
        ]
        
        parsed = urlparse(url)
        return parsed.netloc in youtube_domains
    
    async def _download_youtube(self, url: str, file_path: Path) -> bool:
        """Download audio from YouTube using yt-dlp."""
        
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(file_path.with_suffix('')),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Check if file was created
            if file_path.exists():
                return True
            else:
                logger.error(f"YouTube download failed: {url}")
                return False
                
        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            return False
    
    async def _download_direct(self, url: str, file_path: Path) -> bool:
        """Download file directly using aiohttp."""
        
        try:
            headers = {
                'User-Agent': 'AI-Podcast-Agent/1.0 (https://github.com/your-repo)'
            }
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        return True
                    else:
                        logger.error(f"HTTP {response.status} for {url}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error(f"Download timeout for {url}")
            return False
        except Exception as e:
            logger.error(f"Download error for {url}: {e}")
            return False
    
    def _get_audio_file_path(self, episode: Episode) -> Path:
        """Generate file path for audio file."""
        
        # Get podcast name for directory
        podcast_name = episode.podcast.name.replace(' ', '_').lower()
        
        # Create filename from episode title and date
        safe_title = "".join(c for c in episode.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:100]  # Limit length
        
        date_str = episode.published_date.strftime('%Y-%m-%d')
        filename = f"{date_str}-{safe_title}.mp3"
        
        return Path(self.config.audio_storage_path) / podcast_name / filename 