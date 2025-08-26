# 📧 Email Configuration Guide

## Setting Up Email Delivery

To receive AI podcast digests via email, follow these steps:

### 1. Create a .env file

Create a file named `.env` in your project root with the following content:

```env
# Email Configuration
EMAIL_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com

# Database
DATABASE_URL=sqlite:///data/db.sqlite

# AI Model settings
LOCAL_LLM_MODEL=llama3.1:8b
WHISPER_MODEL=base
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Storage paths
AUDIO_STORAGE_PATH=data/audio
TRANSCRIPT_STORAGE_PATH=data/transcripts
SUMMARY_STORAGE_PATH=data/summaries
EMBEDDING_STORAGE_PATH=data/embeddings

# Processing settings
MAX_CONCURRENT_DOWNLOADS=3
MAX_CONCURRENT_TRANSCRIPTIONS=2
MAX_CONCURRENT_SUMMARIES=2
BATCH_SIZE=10

# Scheduling settings
FEED_CHECK_INTERVAL_HOURS=6
DIGEST_SEND_TIME=08:00
DIGEST_TIMEZONE=UTC

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/podcast_agent.log
```

### 2. Gmail Setup (Recommended)

#### Option A: Use Gmail App Password (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password in `EMAIL_PASSWORD`

#### Option B: Use Gmail with "Less Secure Apps" (Not Recommended)
- Enable "Less secure app access" in Gmail settings
- Use your regular Gmail password

### 3. Other Email Providers

#### Outlook/Hotmail:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### Yahoo:
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### Custom SMTP:
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

### 4. Configuration Details

- **EMAIL_USER**: Your email address (e.g., `yourname@gmail.com`)
- **EMAIL_PASSWORD**: Your app password or email password
- **RECIPIENT_EMAIL**: Where to send the digest (can be the same as EMAIL_USER)
- **DIGEST_SEND_TIME**: When to send daily digest (24-hour format, e.g., `08:00` for 8 AM)

### 5. Test Your Configuration

After setting up the .env file, test the email configuration:

```bash
python test_email_digest.py
```

### 6. Manual Email Test

To test sending an email immediately:

```bash
python -c "
from src.core.config import Settings
from src.workers.digest_composer import DigestComposer
config = Settings()
composer = DigestComposer(config)
episodes = composer.get_recent_episodes(days=7)
if episodes:
    composer.send_digest(episodes)
    print('Email sent successfully!')
else:
    print('No episodes found to send')
"
```

### 7. Schedule Daily Digests

To run the system with scheduled daily digests:

```bash
python -m src.main --scheduler
```

This will:
- Check for new episodes every 6 hours
- Process transcripts and summaries
- Send daily digest at 8:00 AM (or your configured time)

### Troubleshooting

#### Common Issues:

1. **Authentication Error**: 
   - Check your email/password
   - Ensure 2FA is enabled and you're using an app password

2. **Connection Error**:
   - Check SMTP server and port
   - Verify firewall settings

3. **No Episodes Found**:
   - Run the pipeline first to generate content
   - Check database for episodes with summaries

#### Test Commands:

```bash
# Test email configuration
python test_email_digest.py

# Test digest preview
python test_digest_preview.py

# Run full pipeline
python -m src.main
```

### Security Notes

- Never commit your .env file to version control
- Use app passwords instead of regular passwords
- Consider using environment variables for production 