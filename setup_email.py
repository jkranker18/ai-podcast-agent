"""
Interactive email setup script.
"""

import os
from pathlib import Path


def setup_email_config():
    """Interactive email configuration setup."""
    print("📧 Email Configuration Setup")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists. This will update your email settings.")
        response = input("Continue? (y/n): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    print("\nLet's configure your email settings:")
    
    # Email provider selection
    print("\n1. Email Provider:")
    print("   1. Gmail (Recommended)")
    print("   2. Outlook/Hotmail")
    print("   3. Yahoo")
    print("   4. Custom SMTP")
    
    provider_choice = input("Select provider (1-4): ").strip()
    
    if provider_choice == "1":
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
    elif provider_choice == "2":
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = "587"
    elif provider_choice == "3":
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = "587"
    elif provider_choice == "4":
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = input("Enter SMTP port (usually 587): ").strip()
    else:
        print("Invalid choice. Using Gmail.")
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
    
    # Email details
    email_user = input("\n2. Your email address: ").strip()
    email_password = input("3. Your email password or app password: ").strip()
    recipient_email = input("4. Recipient email (can be same as above): ").strip()
    
    if not recipient_email:
        recipient_email = email_user
    
    # Digest time
    digest_time = input("5. Daily digest time (24-hour format, e.g., 08:00): ").strip()
    if not digest_time:
        digest_time = "08:00"
    
    # Create .env content
    env_content = f"""# Email Configuration
EMAIL_ENABLED=true
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
EMAIL_USER={email_user}
EMAIL_PASSWORD={email_password}
RECIPIENT_EMAIL={recipient_email}

# Database
DATABASE_URL=sqlite:///data/db.sqlite

# AI Model settings
LOCAL_LLM_MODEL=llama3.1:8b
WHISPER_MODEL=base
EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI settings (for fallback)
OPENAI_API_KEY=

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
DIGEST_SEND_TIME={digest_time}
DIGEST_TIMEZONE=UTC

# Logging settings
LOG_LEVEL=INFO
LOG_FILE=logs/podcast_agent.log
"""
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        print(f"\n✅ .env file created successfully!")
        print(f"📧 Email: {email_user}")
        print(f"📧 Recipient: {recipient_email}")
        print(f"📧 SMTP: {smtp_server}:{smtp_port}")
        print(f"⏰ Digest time: {digest_time}")
        
        print(f"\n🔐 Security Note:")
        print(f"   - Your email password is stored in .env file")
        print(f"   - For Gmail, use an App Password (recommended)")
        print(f"   - Never commit .env to version control")
        
        print(f"\n🧪 Next Steps:")
        print(f"   1. Test email configuration: python test_email_digest.py")
        print(f"   2. Run full pipeline: python -m src.main")
        print(f"   3. Schedule daily digests: python -m src.main --scheduler")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")


if __name__ == "__main__":
    setup_email_config() 