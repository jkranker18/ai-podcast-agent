# AI Podcast Agent

An intelligent podcast listener that automatically ingests AI/tech podcast episodes, generates summaries, and delivers daily digests via email and Slack.

## Features

- **Automated RSS ingestion** from curated AI/tech podcasts
- **Local-first processing** using open-source models
- **High-quality summaries** generated with local LLMs
- **Daily digest delivery** via email and Slack
- **Interactive chat agent** for Q&A over podcast content
- **Modular architecture** for easy extension

## Supported Podcasts

1. AI Today Podcast
2. CEO AI Podcast  
3. Latent Space
4. Practical AI
5. The Cognitive Revolution

## Quick Start

### Prerequisites

- Python 3.9+
- FFmpeg (for audio processing)
- Optional: NVIDIA GPU with CUDA for faster processing

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd podcastai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
python -m src.database.init_db
```

5. Start the system:
```bash
python -m src.main
```

## Configuration

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=sqlite:///data/db.sqlite

# Email settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=digest@example.com

# Slack settings
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#podcast-digest

# AI Models
LOCAL_LLM_MODEL=llama3.1:8b
WHISPER_MODEL=medium
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Storage paths
AUDIO_STORAGE_PATH=./data/audio
TRANSCRIPT_STORAGE_PATH=./data/transcripts
SUMMARY_STORAGE_PATH=./data/summaries
```

## Architecture

```
Scheduler ─┬─► Feed Fetcher ─► Episode Registry
           ├─► Download Worker ─► Audio Store  
           ├─► ASR Worker ─► Transcript Store
           ├─► Summarizer Worker ─► Summaries
           └─► Digest Composer ─► Email + Slack
                                    │
                                    └─► Chat Agent (RAG)
```

## Usage

### Daily Digest

The system automatically:
1. Checks for new podcast episodes
2. Downloads and transcribes audio
3. Generates summaries and highlights
4. Sends daily digest via email and Slack

### Chat Agent

Access the interactive Q&A system:

```bash
python -m src.chat.agent
```

Ask questions about podcast content, get insights, and explore topics discussed in episodes.

## Development

### Project Structure

```
src/
├── core/           # Core functionality
├── database/       # Database models and operations
├── fetchers/       # RSS and audio fetchers
├── processors/     # ASR, summarization, embeddings
├── delivery/       # Email and Slack delivery
├── chat/          # RAG-based chat agent
└── main.py        # Application entry point

data/
├── audio/         # Downloaded audio files
├── transcripts/   # Generated transcripts
├── summaries/     # Episode summaries
└── db.sqlite      # SQLite database
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## Legal Notice

This tool is for personal use only. Please respect each podcast's Terms of Service and copyright. Do not redistribute transcripts or content without permission.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details. 