# AI Podcast Agent

Automatically ingests new podcast episodes from curated AI/tech shows, generates high-quality summaries and highlights, and delivers a daily digest via Email and Slack.

## Features

- **RSS Feed Monitoring**: Automatically checks for new episodes from AI/tech podcasts
- **Audio Processing**: Downloads and transcribes audio files using Whisper
- **AI Summarization**: Generates executive summaries using local Llama 3.1 model
- **Daily Digest**: Sends formatted email summaries to subscribers
- **Local-First**: Runs entirely on your local machine or GitHub Actions

## Current Status

**Last updated**: 2025-08-29 - System operational and running daily at 6:00 AM Eastern

## Podcasts Monitored

- AI Today Podcast
- The TWIML AI Podcast  
- Practical AI
- Lex Fridman Podcast

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Run: `python run_scheduler.py`

## GitHub Actions

The system runs automatically via GitHub Actions every day at 6:00 AM Eastern (11:00 AM UTC). 