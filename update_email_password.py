"""
Script to update email password in .env file.
"""

def update_email_password():
    """Update the email password in .env file."""
    print("🔐 Update Email Password")
    print("=" * 30)
    
    print("Please enter your Gmail App Password:")
    print("(This is the 16-character password from Google Account settings)")
    print("Format: xxxx xxxx xxxx xxxx")
    
    app_password = input("App Password: ").strip()
    
    if not app_password:
        print("❌ No password entered")
        return
    
    # Read current .env file
    try:
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace the password line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("EMAIL_PASSWORD="):
                lines[i] = f"EMAIL_PASSWORD={app_password}"
                break
        
        # Write back to .env
        with open(".env", "w") as f:
            f.write('\n'.join(lines))
        
        print("✅ Email password updated successfully!")
        print("🧪 You can now test email sending:")
        print("   python test_send_email.py")
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")


if __name__ == "__main__":
    update_email_password() 