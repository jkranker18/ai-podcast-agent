"""
Summarization Worker

Uses local LLM (Ollama) to generate summaries and key insights from podcast transcripts.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import ollama
from loguru import logger
from sqlalchemy.orm import Session

from src.core.config import Settings
from src.database.models import Episode, Summary, ProcessingJob
from src.database.init_db import get_db_session


class SummarizationWorker:
    """Worker for generating summaries using local LLM."""
    
    def __init__(self, config: Settings):
        self.config = config
        self.executor = ThreadPoolExecutor(max_workers=config.max_concurrent_summaries)
        self.model_name = config.local_llm_model
        
    def _load_transcript(self, transcript_file_path: str) -> Dict:
        """Load transcript data from JSON file."""
        try:
            with open(transcript_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading transcript {transcript_file_path}: {e}")
            raise
    
    def _create_summary_prompt(self, transcript_data: Dict, episode_title: str) -> str:
        """Create a prompt for summarization."""
        
        # Extract full transcript
        full_transcript = transcript_data.get('full_transcript', '')
        
        # Create a comprehensive prompt for summarization
        prompt = f"""You are an AI assistant tasked with creating a comprehensive summary of a podcast episode about AI and technology.

Episode Title: {episode_title}
Duration: {transcript_data.get('duration', 0):.1f} seconds
Word Count: {transcript_data.get('word_count', 0)} words

Please analyze the following transcript and provide:

1. **Executive Summary** (2-3 paragraphs): A high-level overview of the main topics, key insights, and value proposition of this episode.

2. **Key Points** (5-8 bullet points): The most important takeaways, insights, or actionable advice from the episode.

3. **Topics Discussed** (list): Main themes, technologies, or concepts covered in the episode.

4. **Highlights** (3-5 items): Notable quotes, insights, or moments with approximate timestamps.

5. **Sentiment**: Overall tone (positive, negative, neutral, or mixed).

Please format your response as JSON with the following structure:
{{
    "executive_summary": "detailed summary here",
    "key_points": ["point 1", "point 2", "point 3"],
    "topics": ["topic 1", "topic 2", "topic 3"],
    "highlights": [
        {{"timestamp": "00:00", "text": "highlight text", "context": "brief context"}}
    ],
    "sentiment": "positive/negative/neutral/mixed"
}}

Transcript:
{full_transcript[:8000]}  # Limit to first 8000 chars to avoid token limits
"""
        return prompt
    
    def _generate_summary(self, prompt: str) -> Dict:
        """Generate summary using Ollama."""
        try:
            logger.info(f"Generating summary using model: {self.model_name}")
            
            # Use Ollama to generate summary
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.3,  # Lower temperature for more focused summaries
                    'top_p': 0.9,
                    'num_predict': 2048  # Limit response length
                }
            )
            
            # Extract the response content
            summary_text = response['message']['content']
            
            # Try to parse as JSON
            try:
                # Look for JSON in the response
                start_idx = summary_text.find('{')
                end_idx = summary_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = summary_text[start_idx:end_idx]
                    summary_data = json.loads(json_str)
                else:
                    # Fallback: create structured summary from text
                    summary_data = {
                        "executive_summary": summary_text,
                        "key_points": [],
                        "topics": [],
                        "highlights": [],
                        "sentiment": "neutral"
                    }
                
                return summary_data
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                # Fallback: create structured summary from text
                return {
                    "executive_summary": summary_text,
                    "key_points": [],
                    "topics": [],
                    "highlights": [],
                    "sentiment": "neutral"
                }
                
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            raise
    
    def _save_summary(self, episode_id: int, summary_data: Dict) -> str:
        """Save summary to file and return the file path."""
        try:
            # Create summary directory
            summary_dir = Path(self.config.summary_storage_path)
            summary_dir.mkdir(parents=True, exist_ok=True)
            
            # Create summary file path
            summary_file = summary_dir / f"episode_{episode_id}_summary.json"
            
            # Add metadata
            summary_with_metadata = {
                "episode_id": episode_id,
                "generated_at": datetime.utcnow().isoformat(),
                "model_used": self.model_name,
                "summary_data": summary_data
            }
            
            # Save summary as JSON
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_with_metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Summary saved to: {summary_file}")
            return str(summary_file)
            
        except Exception as e:
            logger.error(f"Error saving summary for episode {episode_id}: {e}")
            raise
    
    def process_episode(self, episode: Episode, db: Session) -> bool:
        """Process a single episode for summarization."""
        try:
            # Check if episode has transcript
            if not episode.transcript_file_path or not os.path.exists(episode.transcript_file_path):
                logger.warning(f"No transcript found for episode {episode.id}")
                return False
            
            # Check if already summarized
            if episode.summary_file_path and os.path.exists(episode.summary_file_path):
                logger.info(f"Episode {episode.id} already summarized")
                return True
            
            # Create processing job
            job = ProcessingJob(
                episode_id=episode.id,
                job_type="summarization",
                status="processing"
            )
            db.add(job)
            
            try:
                # Load transcript
                transcript_data = self._load_transcript(episode.transcript_file_path)
                
                # Create summary prompt
                prompt = self._create_summary_prompt(transcript_data, episode.title)
                
                # Generate summary
                summary_data = self._generate_summary(prompt)
                
                # Save summary
                summary_file_path = self._save_summary(episode.id, summary_data)
                
                # Create summary record
                summary = Summary(
                    episode_id=episode.id,
                    executive_summary=summary_data.get("executive_summary", ""),
                    key_points=json.dumps(summary_data.get("key_points", [])),
                    highlights=json.dumps(summary_data.get("highlights", [])),
                    topics=json.dumps(summary_data.get("topics", [])),
                    sentiment=summary_data.get("sentiment", "neutral"),
                    summary_length=len(summary_data.get("executive_summary", "")),
                    model_used=self.model_name
                )
                db.add(summary)
                
                # Update episode
                episode.summary_file_path = summary_file_path
                episode.summarized = True
                
                # Update job status
                job.status = "completed"
                job.result = f"Generated summary with {summary_data.get('key_points', [])} key points"
                
                logger.info(f"Successfully summarized episode {episode.id}")
                return True
                
            except Exception as e:
                # Update job status on error
                job.status = "failed"
                job.error_message = str(e)
                logger.error(f"Failed to summarize episode {episode.id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing episode {episode.id}: {e}")
            return False
    
    async def process_pending_episodes(self) -> Dict:
        """Process all episodes that need summarization."""
        logger.info("Starting summarization of pending episodes...")
        
        with get_db_session() as db:
            # Get episodes that need summarization
            episodes = db.query(Episode).filter(
                Episode.transcript_file_path.isnot(None),
                Episode.summary_file_path.is_(None)
            ).all()
            
            if not episodes:
                logger.info("No episodes need summarization")
                return {"processed": 0, "successful": 0, "failed": 0}
            
            logger.info(f"Found {len(episodes)} episodes to summarize")
            
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
            
            logger.info(f"Summarization completed: {successful} successful, {failed} failed")
            
            return {
                "processed": len(episodes),
                "successful": successful,
                "failed": failed
            }
    
    def get_summarization_stats(self) -> Dict:
        """Get statistics about summarization status."""
        with get_db_session() as db:
            total_episodes = db.query(Episode).filter(Episode.transcript_file_path.isnot(None)).count()
            summarized_episodes = db.query(Episode).filter(
                Episode.transcript_file_path.isnot(None),
                Episode.summary_file_path.isnot(None)
            ).count()
            
            return {
                "total_episodes_with_transcripts": total_episodes,
                "summarized_episodes": summarized_episodes,
                "pending_summarization": total_episodes - summarized_episodes,
                "completion_rate": (summarized_episodes / total_episodes * 100) if total_episodes > 0 else 0
            } 