"""
Test script for summarization functionality.
"""

import asyncio
import os
import json

from src.core.config import Settings
from src.core.logger import setup_logging
from src.workers.summarization_worker import SummarizationWorker


async def test_summarization():
    """Test summarization with existing transcript."""
    print("🧠 Testing Local LLM Summarization")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    worker = SummarizationWorker(config)
    
    # Test with our existing transcript
    transcript_file = "data/transcripts/episode_999_transcript.json"
    
    if os.path.exists(transcript_file):
        print(f"Testing summarization of: {transcript_file}")
        
        try:
            # Load transcript
            transcript_data = worker._load_transcript(transcript_file)
            print(f"✅ Transcript loaded: {transcript_data['word_count']} words")
            
            # Create summary prompt
            prompt = worker._create_summary_prompt(transcript_data, "Dr. Lukasz Kowalczyk on Practical AI Adoption in Healthcare")
            print(f"✅ Summary prompt created ({len(prompt)} characters)")
            
            # Generate summary
            print("🤖 Generating summary with local LLM...")
            summary_data = worker._generate_summary(prompt)
            
            print("✅ Summary generated successfully!")
            print(f"Executive Summary: {summary_data.get('executive_summary', '')[:200]}...")
            print(f"Key Points: {len(summary_data.get('key_points', []))} points")
            print(f"Topics: {summary_data.get('topics', [])}")
            print(f"Sentiment: {summary_data.get('sentiment', 'unknown')}")
            
            # Save summary
            summary_file = worker._save_summary(999, summary_data)
            print(f"💾 Summary saved to: {summary_file}")
            
            # Show full summary
            print("\n📋 Full Summary:")
            print("=" * 30)
            print(f"Executive Summary:\n{summary_data.get('executive_summary', '')}")
            print(f"\nKey Points:")
            for i, point in enumerate(summary_data.get('key_points', []), 1):
                print(f"  {i}. {point}")
            print(f"\nTopics: {', '.join(summary_data.get('topics', []))}")
            print(f"Sentiment: {summary_data.get('sentiment', 'unknown')}")
            
        except Exception as e:
            print(f"❌ Summarization error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Transcript file not found: {transcript_file}")


if __name__ == "__main__":
    asyncio.run(test_summarization()) 