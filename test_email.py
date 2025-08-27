#!/usr/bin/env python3
"""
Test email configuration and send a test email.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email_config():
    """Test email configuration and send a test email."""
    
    # Load configuration from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    email_user = os.getenv('EMAIL_USER', '')
    email_password = os.getenv('EMAIL_PASSWORD', '')
    subscriber_emails = os.getenv('SUBSCRIBER_EMAILS', '')
    email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
    
    print("📧 Email Configuration Test")
    print("=" * 40)
    print(f"Email enabled: {email_enabled}")
    print(f"SMTP server: {smtp_server}")
    print(f"SMTP port: {smtp_port}")
    print(f"Email user: {email_user}")
    print(f"Subscriber emails: {subscriber_emails}")
    print(f"Email password set: {'Yes' if email_password else 'No'}")
    
    if not email_enabled:
        print("❌ Email is disabled")
        return False
    
    if not email_user or not email_password or not subscriber_emails:
        print("❌ Missing required email configuration")
        return False
    
    # Parse subscriber emails
    subscribers = [email.strip() for email in subscriber_emails.split(',') if email.strip()]
    if not subscribers:
        print("❌ No valid subscriber emails found")
        return False
    
    print(f"📧 Sending test email to {len(subscribers)} subscribers...")
    
    try:
        # Create test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"AI Podcast Agent - Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg['From'] = email_user
        msg['To'] = ', '.join(subscribers)
        
        # Create test content
        text_content = f"""
AI Podcast Agent Test Email

This is a test email from your AI Podcast Agent.

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Configuration:
- SMTP Server: {smtp_server}
- SMTP Port: {smtp_port}
- Email User: {email_user}
- Subscribers: {subscriber_emails}

If you receive this email, your email configuration is working correctly!

Best regards,
AI Podcast Agent
"""
        
        html_content = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .content {{ margin: 20px 0; }}
        .footer {{ color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>🎙️ AI Podcast Agent - Test Email</h2>
    </div>
    
    <div class="content">
        <p>This is a test email from your AI Podcast Agent.</p>
        
        <h3>Test Details:</h3>
        <ul>
            <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            <li><strong>SMTP Server:</strong> {smtp_server}</li>
            <li><strong>SMTP Port:</strong> {smtp_port}</li>
            <li><strong>Email User:</strong> {email_user}</li>
            <li><strong>Subscribers:</strong> {subscriber_emails}</li>
        </ul>
        
        <p>✅ If you receive this email, your email configuration is working correctly!</p>
    </div>
    
    <div class="footer">
        <p>Best regards,<br>AI Podcast Agent</p>
    </div>
</body>
</html>
"""
        
        # Attach both HTML and text versions
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            print(f"🔗 Connecting to {smtp_server}:{smtp_port}...")
            server.starttls()
            print("🔐 Starting TLS...")
            server.login(email_user, email_password)
            print("✅ Login successful")
            
            for subscriber in subscribers:
                try:
                    server.send_message(msg)
                    print(f"✅ Test email sent to {subscriber}")
                except Exception as e:
                    print(f"❌ Failed to send to {subscriber}: {e}")
        
        print("🎉 Email test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    test_email_config() 