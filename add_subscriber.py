#!/usr/bin/env python3

import os
import re
from pathlib import Path

def validate_email(email):
    """Simple email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def add_subscriber():
    """Add a new subscriber to the email digest."""
    
    print("📧 Add New Email Subscriber")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please run setup_email.py first to configure email settings.")
        return
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Find current subscriber_emails line
    subscriber_line_index = None
    current_subscribers = []
    
    for i, line in enumerate(lines):
        if line.startswith('SUBSCRIBER_EMAILS='):
            subscriber_line_index = i
            value = line.split('=', 1)[1].strip()
            if value:
                current_subscribers = [email.strip() for email in value.split(',')]
            break
    
    # Show current subscribers
    if current_subscribers:
        print(f"📋 Current subscribers ({len(current_subscribers)}):")
        for email in current_subscribers:
            print(f"  • {email}")
        print()
    else:
        print("📋 No current subscribers configured")
        print()
    
    # Get new subscriber email
    while True:
        new_email = input("Enter new subscriber email address: ").strip()
        
        if not new_email:
            print("❌ Email address cannot be empty")
            continue
        
        if not validate_email(new_email):
            print("❌ Please enter a valid email address")
            continue
        
        if new_email in current_subscribers:
            print("❌ This email is already subscribed")
            continue
        
        break
    
    # Add to subscribers list
    current_subscribers.append(new_email)
    
    # Update .env file
    subscriber_value = ','.join(current_subscribers)
    
    if subscriber_line_index is not None:
        # Update existing line
        lines[subscriber_line_index] = f"SUBSCRIBER_EMAILS={subscriber_value}\n"
    else:
        # Add new line
        lines.append(f"SUBSCRIBER_EMAILS={subscriber_value}\n")
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✅ Successfully added {new_email}")
    print(f"📧 Total subscribers: {len(current_subscribers)}")
    print()
    print("📋 Updated subscriber list:")
    for email in current_subscribers:
        print(f"  • {email}")
    print()
    print("🔄 The system will use these subscribers for the next digest!")

if __name__ == "__main__":
    add_subscriber() 