"""
Digest Composer

Composes daily email digests from podcast summaries and sends them via SMTP.
"""

import smtplib
import json
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger

from src.core.config import Settings
from src.database.models import Episode, Summary, Podcast
from src.database.init_db import get_db_session


class DigestComposer:
    """Composes and sends daily email digests."""
    
    def __init__(self, config: Settings):
        self.config = config
        
    def _load_summary(self, summary_file_path: str) -> Dict[str, Any]:
        """Load summary data from JSON file."""
        try:
            with open(summary_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading summary from {summary_file_path}: {e}")
            return {}
    
    def _load_email_template(self) -> str:
        """Load the custom email template."""
        template_path = Path("email-template.html")
        if not template_path.exists():
            logger.error("Email template not found: email-template.html")
            return ""
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading email template: {e}")
            return ""
    
    def _format_episode_summary(self, episode: Episode, summary_data: Dict[str, Any]) -> str:
        """Format a single episode summary for HTML."""
        summary = summary_data.get('summary_data', {})
        
        episode_html = f"""
        <div class="episode-card">
            <h3>🎙️ {episode.title}</h3>
            <p class="episode-meta">
                <strong>Podcast:</strong> {episode.podcast.name} | 
                <strong>Duration:</strong> {episode.transcript_duration/60:.1f} min | 
                <strong>Published:</strong> {episode.published_date.strftime('%B %d, %Y')}
            </p>
            
            <div style="margin-bottom: 20px;">
                <h4 class="section-title">📋 Executive Summary</h4>
                <p>{summary.get('executive_summary', 'No summary available')}</p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4 class="section-title">🔑 Key Points</h4>
                <ul>
        """
        
        for point in summary.get('key_points', []):
            episode_html += f"                    <li>{point}</li>\n"
        
        episode_html += f"""
                </ul>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4 class="section-title">🏷️ Topics</h4>
                <p class="topics">{', '.join(summary.get('topics', []))}</p>
            </div>
            
            <div style="text-align: right;">
                <span class="sentiment-badge">{summary.get('sentiment', 'neutral').upper()}</span>
            </div>
        </div>
        """
        
        return episode_html
    
    def _create_digest_html(self, episodes: List[Episode], date: datetime) -> str:
        """Create HTML email digest using custom template."""
        
        # Load the custom template
        template = self._load_email_template()
        if not template:
            logger.error("Failed to load email template, falling back to built-in template")
            return self._create_digest_html_fallback(episodes, date)
        
        # Calculate stats
        episode_count = len(episodes)
        word_count = sum(ep.transcript_word_count or 0 for ep in episodes)
        duration_minutes = sum(ep.transcript_duration or 0 for ep in episodes) / 60
        
        # Replace template variables
        template = template.replace("{{date}}", date.strftime('%B %d, %Y'))
        template = template.replace("{{episode_count}}", str(episode_count))
        template = template.replace("{{word_count}}", f"{word_count:,}")
        template = template.replace("{{duration_minutes}}", f"{duration_minutes:.1f}")
        
        # Find the position to insert episode content (after the stats div)
        stats_end = template.find('</div>', template.find('<div class="stats">'))
        if stats_end == -1:
            logger.error("Could not find stats div in template")
            return self._create_digest_html_fallback(episodes, date)
        
        # Insert episode content
        episode_content = ""
        for episode in episodes:
            try:
                if episode.summary_file_path and Path(episode.summary_file_path).exists():
                    summary_data = self._load_summary(episode.summary_file_path)
                    episode_html = self._format_episode_summary(episode, summary_data)
                    episode_content += episode_html
                else:
                    logger.warning(f"No summary found for episode {episode.id}")
            except Exception as e:
                logger.error(f"Error formatting episode {episode.id}: {e}")
                continue
        
        # Insert episode content after stats div
        template = template[:stats_end + 6] + "\n\n" + episode_content + "\n\n" + template[stats_end + 6:]
        
        return template
    
    def _create_digest_html_fallback(self, episodes: List[Episode], date: datetime) -> str:
        """Fallback to built-in HTML template if custom template fails."""
        logger.warning("Using fallback HTML template")
        
        # Header
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Podcast Digest - {date.strftime('%B %d, %Y')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
                .stats {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">🤖 AI Podcast Digest</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Your daily dose of AI insights from top podcasts</p>
                <p style="margin: 5px 0 0 0; font-size: 16px; opacity: 0.8;">{date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="stats">
                <h3 style="margin-top: 0; color: #333;">📊 Today's Summary</h3>
                <p style="margin: 5px 0; color: #666;">
                    <strong>{len(episodes)} episodes</strong> processed | 
                    <strong>{sum(ep.transcript_word_count or 0 for ep in episodes):,} words</strong> transcribed | 
                    <strong>{sum(ep.transcript_duration or 0 for ep in episodes)/60:.1f} minutes</strong> of content
                </p>
            </div>
        """
        
        # Add episode summaries
        for episode in episodes:
            try:
                if episode.summary_file_path and Path(episode.summary_file_path).exists():
                    summary_data = self._load_summary(episode.summary_file_path)
                    episode_html = self._format_episode_summary(episode, summary_data)
                    html_content += episode_html
                else:
                    logger.warning(f"No summary found for episode {episode.id}")
            except Exception as e:
                logger.error(f"Error formatting episode {episode.id}: {e}")
                continue
        
        # Footer
        html_content += f"""
            <div class="footer">
                <p>🤖 Generated by AI Podcast Agent</p>
                <p>Powered by Whisper + Llama 3.1 | Local-first AI processing</p>
                <p style="font-size: 12px; margin-top: 10px;">
                    This digest contains AI-generated summaries. Please verify important information from original sources.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _create_digest_text(self, episodes: List[Episode], date: datetime) -> str:
        """Create plain text email digest."""
        
        text_content = f"""
AI Podcast Digest - {date.strftime('%B %d, %Y')}
{'=' * 50}

Your daily dose of AI insights from top podcasts

TODAY'S SUMMARY:
- {len(episodes)} episodes processed
- {sum(ep.transcript_word_count or 0 for ep in episodes):,} words transcribed
- {sum(ep.transcript_duration or 0 for ep in episodes)/60:.1f} minutes of content

"""
        
        for episode in episodes:
            try:
                if episode.summary_file_path and Path(episode.summary_file_path).exists():
                    summary_data = self._load_summary(episode.summary_file_path)
                    summary = summary_data.get('summary_data', {})
                    
                    text_content += f"""
🎙️ {episode.title}
Podcast: {episode.podcast.name}
Duration: {episode.transcript_duration/60:.1f} min
Published: {episode.published_date.strftime('%B %d, %Y')}

📋 Executive Summary:
{summary.get('executive_summary', 'No summary available')}

🔑 Key Points:
"""
                    for i, point in enumerate(summary.get('key_points', []), 1):
                        text_content += f"  {i}. {point}\n"
                    
                    text_content += f"""
🏷️ Topics: {', '.join(summary.get('topics', []))}
Sentiment: {summary.get('sentiment', 'neutral').upper()}

{'-' * 50}
"""
                else:
                    logger.warning(f"No summary found for episode {episode.id}")
            except Exception as e:
                logger.error(f"Error formatting episode {episode.id}: {e}")
                continue
        
        text_content += f"""
Generated by AI Podcast Agent
Powered by Whisper + Llama 3.1 | Local-first AI processing

This digest contains AI-generated summaries. Please verify important information from original sources.
"""
        
        return text_content
    
    def get_recent_episodes(self, days: int = 1) -> List[Episode]:
        """Get episodes from the last N days that have summaries."""
        with get_db_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            episodes = session.query(Episode).join(Podcast).filter(
                Episode.summary_file_path.isnot(None),
                Episode.published_date >= cutoff_date
            ).order_by(Episode.published_date.desc()).all()
            
            # Ensure episodes are loaded within the session
            for episode in episodes:
                session.refresh(episode)
                session.refresh(episode.podcast)
            
            return episodes
    
    def _get_subscriber_list(self) -> List[str]:
        """Get list of subscriber email addresses."""
        subscribers = []
        
        # Add legacy single recipient if set
        if self.config.recipient_email:
            subscribers.append(self.config.recipient_email.strip())
        
        # Add multiple subscribers from comma-separated list
        if self.config.subscriber_emails:
            for email in self.config.subscriber_emails.split(','):
                email = email.strip()
                if email and email not in subscribers:
                    subscribers.append(email)
        
        return subscribers
    
    def _send_digest_content(self, html_content: str, text_content: str, date: datetime) -> bool:
        """Send email digest with pre-created content."""
        if not self.config.email_enabled:
            logger.warning("Email is disabled in configuration")
            return False
        
        # Get list of subscribers
        subscribers = self._get_subscriber_list()
        if not subscribers:
            logger.warning("No email subscribers configured")
            return False
        
        try:
            # Send to each subscriber
            success_count = 0
            for subscriber in subscribers:
                try:
                    # Create email message for this subscriber
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f"AI Podcast Digest - {date.strftime('%B %d, %Y')}"
                    msg['From'] = self.config.email_user
                    msg['To'] = subscriber
                    
                    # Attach both HTML and text versions
                    text_part = MIMEText(text_content, 'plain')
                    html_part = MIMEText(html_content, 'html')
                    
                    msg.attach(text_part)
                    msg.attach(html_part)
                    
                    # Send email
                    with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                        server.starttls()
                        server.login(self.config.email_user, self.config.email_password)
                        server.send_message(msg)
                    
                    logger.info(f"Digest sent successfully to {subscriber}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending digest to {subscriber}: {e}")
                    continue
            
            if success_count > 0:
                logger.info(f"Digest sent to {success_count}/{len(subscribers)} subscribers")
                return True
            else:
                logger.error("Failed to send digest to any subscribers")
                return False
            
        except Exception as e:
            logger.error(f"Error in send_digest: {e}")
            return False
    
    def send_digest(self, episodes: List[Episode], date: datetime = None) -> bool:
        """Send email digest to all subscribers."""
        if not self.config.email_enabled:
            logger.warning("Email is disabled in configuration")
            return False
        
        if not episodes:
            logger.info("No episodes to include in digest")
            return False
        
        if date is None:
            date = datetime.utcnow()
        
        # Get list of subscribers
        subscribers = self._get_subscriber_list()
        if not subscribers:
            logger.warning("No email subscribers configured")
            return False
        
        try:
            # Create email content
            html_content = self._create_digest_html(episodes, date)
            text_content = self._create_digest_text(episodes, date)
            
            # Send to each subscriber
            success_count = 0
            for subscriber in subscribers:
                try:
                    # Create email message for this subscriber
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = f"AI Podcast Digest - {date.strftime('%B %d, %Y')}"
                    msg['From'] = self.config.email_user
                    msg['To'] = subscriber
                    
                    # Attach both HTML and text versions
                    text_part = MIMEText(text_content, 'plain')
                    html_part = MIMEText(html_content, 'html')
                    
                    msg.attach(text_part)
                    msg.attach(html_part)
                    
                    # Send email
                    with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                        server.starttls()
                        server.login(self.config.email_user, self.config.email_password)
                        server.send_message(msg)
                    
                    logger.info(f"Digest sent successfully to {subscriber}")
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error sending digest to {subscriber}: {e}")
                    continue
            
            if success_count > 0:
                logger.info(f"Digest sent to {success_count}/{len(subscribers)} subscribers")
                return True
            else:
                logger.error("Failed to send digest to any subscribers")
                return False
            
        except Exception as e:
            logger.error(f"Error in send_digest: {e}")
            return False
    
    async def send_daily_digest(self) -> bool:
        """Send daily digest with recent episodes."""
        logger.info("Composing and sending daily digest...")
        
        try:
            # Get episodes and create digest within a single session
            with get_db_session() as session:
                cutoff_date = datetime.utcnow() - timedelta(hours=25)
                
                episodes = session.query(Episode).join(Podcast).filter(
                    Episode.summary_file_path.isnot(None),
                    Episode.summarization_completed_at >= cutoff_date
                ).order_by(Episode.summarization_completed_at.desc()).all()
                
                logger.info(f"Found {len(episodes)} episodes processed in the last 24 hours (since {cutoff_date})")
                
                if not episodes:
                    logger.info("No recent episodes found for daily digest")
                    return True  # Not an error, just no content
                
                # Ensure episodes are loaded within the session
                for episode in episodes:
                    session.refresh(episode)
                    session.refresh(episode.podcast)
                
                # Create digest content within session context
                date = datetime.utcnow()
                html_content = self._create_digest_html(episodes, date)
                text_content = self._create_digest_text(episodes, date)
            
            # Send digest (episodes are no longer needed after content creation)
            success = self._send_digest_content(html_content, text_content, date)
            
            if success:
                logger.info(f"Daily digest sent with {len(episodes)} episodes")
            else:
                logger.error("Failed to send daily digest")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send daily digest: {e}")
            return False 
