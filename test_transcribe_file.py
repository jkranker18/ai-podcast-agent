"""
Test transcription of an existing audio file.
"""

import asyncio
import os
from pathlib import Path

from src.core.config import Settings
from src.core.logger import setup_logging
from src.workers.transcription_worker import TranscriptionWorker


async def test_transcribe_file():
    """Test transcription of a single audio file."""
    print("🎯 Testing Direct File Transcription")
    print("=" * 50)
    
    # Initialize
    config = Settings()
    setup_logging(config.log_level, config.log_file)
    
    worker = TranscriptionWorker(config)
    
    # Test with one of the existing audio files
    audio_file = "data/audio/ai_today_podcast/2025-08-21-Dr_Lukasz_Kowalczyk_on_Practical_AI_Adoption_in_Healthcare.mp3"
    
    if os.path.exists(audio_file):
        print(f"Testing transcription of: {audio_file}")
        print(f"File size: {os.path.getsize(audio_file) / (1024*1024):.1f} MB")
        
        try:
            # Transcribe the audio file directly
            transcript_data = worker.transcribe_audio(audio_file)
            
            print("✅ Transcription completed successfully!")
            print(f"Language: {transcript_data['language']} (confidence: {transcript_data['language_probability']:.2f})")
            print(f"Duration: {transcript_data['duration']:.1f} seconds")
            print(f"Word count: {transcript_data['word_count']}")
            print(f"Segments: {len(transcript_data['segments'])}")
            
            # Show first few segments
            print("\n📝 First few segments:")
            for i, segment in enumerate(transcript_data['segments'][:5]):
                print(f"  {i+1}. [{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text']}")
            
            # Save transcript
            transcript_file = worker.save_transcript(999, transcript_data)  # Use episode ID 999 for test
            print(f"\n💾 Transcript saved to: {transcript_file}")
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
    else:
        print(f"❌ Audio file not found: {audio_file}")


if __name__ == "__main__":
    asyncio.run(test_transcribe_file()) 