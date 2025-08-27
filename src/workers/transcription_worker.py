"""
ASR Transcription Worker

Uses faster-whisper to transcribe audio files and save transcripts to the database.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import json

from faster_whisper import WhisperModel
from loguru import logger
from sqlalchemy.orm import Session

from src.core.config import Settings
from src.database.models import Episode, ProcessingJob
from src.database.init_db import get_db_session


class TranscriptionWorker:
    """Worker for transcribing audio files using Whisper."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_transcriptions)
        
    def _load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.config.whisper_model}")
            self.model = WhisperModel(
                model_size_or_path=self.config.whisper_model,
                device="cpu",  # Use CPU for local processing
                compute_type="int8"  # Use int8 for faster processing
            )
            logger.info("Whisper model loaded successfully")
    
    def transcribe_audio(self, audio_path: str) -> dict:
        """Transcribe a single audio file."""
        try:
            self._load_model()
            
            logger.info(f"Transcribing: {audio_path}")
            
            # Transcribe the audio
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect segments
            transcript_segments = []
            full_transcript = ""
            
            for segment in segments:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": [
                        {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "probability": word.probability
                        }
                        for word in segment.words
                    ] if segment.words else []
                }
                transcript_segments.append(segment_data)
                full_transcript += segment.text + " "
            
            # Create transcript data
            transcript_data = {
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": transcript_segments,
                "full_transcript": full_transcript.strip(),
                "word_count": len(full_transcript.split()),
                "audio_path": audio_path
            }
            
            logger.info(f"Transcription completed: {len(transcript_segments)} segments, {transcript_data['word_count']} words")
            return transcript_data
            
        except Exception as e:
            logger.error(f"Error transcribing {audio_path}: {e}")
            # Return a minimal transcript instead of raising
            logger.warning(f"Skipping transcription for {audio_path} due to error")
            return {
                "language": "en",
                "language_probability": 0.0,
                "duration": 0.0,
                "segments": [],
                "full_transcript": f"[Transcription failed: {str(e)}]",
                "word_count": 0,
                "audio_path": audio_path
            }
    
    def save_transcript(self, episode_id: int, transcript_data: dict) -> str:
        """Save transcript to file and return the file path."""
        try:
            # Create transcript file path
            transcript_dir = Path(self.config.transcript_storage_path)
            transcript_dir.mkdir(parents=True, exist_ok=True)
            
            # Use episode ID for filename
            transcript_file = transcript_dir / f"episode_{episode_id}_transcript.json"
            
            # Save transcript as JSON
            with open(transcript_file, 'w', encoding='utf-8') as f:
                json.dump(transcript_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Transcript saved to: {transcript_file}")
            return str(transcript_file)
            
        except Exception as e:
            logger.error(f"Error saving transcript for episode {episode_id}: {e}")
            raise
    
    def process_episode(self, episode: Episode, db: Session) -> bool:
        """Process a single episode for transcription."""
        try:
            # Check if episode has audio file
            if not episode.audio_file_path or not os.path.exists(episode.audio_file_path):
                logger.warning(f"No audio file found for episode {episode.id}")
                return False
            
            # Check if already transcribed
            if episode.transcript_file_path and os.path.exists(episode.transcript_file_path):
                logger.info(f"Episode {episode.id} already transcribed")
                return True
            
            # Create processing job
            job = ProcessingJob(
                episode_id=episode.id,
                job_type="transcription",
                status="processing"
            )
            db.add(job)
            # Don't commit here - let the context manager handle it
            
            try:
                # Transcribe audio
                transcript_data = self.transcribe_audio(episode.audio_file_path)
                
                # Save transcript
                transcript_file_path = self.save_transcript(episode.id, transcript_data)
                
                # Update episode
                episode.transcript_file_path = transcript_file_path
                episode.transcript_word_count = transcript_data["word_count"]
                episode.transcript_duration = transcript_data["duration"]
                episode.transcript_language = transcript_data["language"]
                
                # Update job status
                job.status = "completed"
                job.result = f"Transcribed {transcript_data['word_count']} words"
                
                # Don't commit here - let the context manager handle it
                logger.info(f"Successfully transcribed episode {episode.id}")
                return True
                
            except Exception as e:
                # Update job status on error
                job.status = "failed"
                job.error_message = str(e)
                # Don't commit here - let the context manager handle it
                logger.error(f"Failed to transcribe episode {episode.id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing episode {episode.id}: {e}")
            return False
    
    async def process_pending_episodes(self) -> dict:
        """Process all episodes that need transcription."""
        logger.info("Starting transcription of pending episodes...")
        
        with get_db_session() as db:
            # Get episodes that need transcription (limit to 3 to avoid timeout)
            episodes = db.query(Episode).filter(
                Episode.audio_file_path.isnot(None),
                Episode.transcript_file_path.is_(None)
            ).limit(3).all()
            
            if not episodes:
                logger.info("No episodes need transcription")
                return {"processed": 0, "successful": 0, "failed": 0}
            
            logger.info(f"Found {len(episodes)} episodes to transcribe")
            
            # Process episodes in parallel using thread pool
            loop = asyncio.get_event_loop()
            tasks = []
            
            for episode in episodes:
                task = loop.run_in_executor(
                    self.executor, 
                    self.process_episode, 
                    episode, 
                    db
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r is True)
            failed = len(results) - successful
            
            logger.info(f"Transcription completed: {successful} successful, {failed} failed")
            
            return {
                "processed": len(episodes),
                "successful": successful,
                "failed": failed
            }
    
    def get_transcription_stats(self) -> dict:
        """Get statistics about transcription status."""
        with get_db_session() as db:
            total_episodes = db.query(Episode).filter(Episode.audio_file_path.isnot(None)).count()
            transcribed_episodes = db.query(Episode).filter(
                Episode.audio_file_path.isnot(None),
                Episode.transcript_file_path.isnot(None)
            ).count()
            
            return {
                "total_episodes_with_audio": total_episodes,
                "transcribed_episodes": transcribed_episodes,
                "pending_transcription": total_episodes - transcribed_episodes,
                "completion_rate": (transcribed_episodes / total_episodes * 100) if total_episodes > 0 else 0
            } 