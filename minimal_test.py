#!/usr/bin/env python3
"""
Minimal test using only Python standard library.
"""

print("🚀 Minimal test starting...")

try:
    import os
    print("✅ os imported")
    
    import sys
    print("✅ sys imported")
    
    import json
    print("✅ json imported")
    
    import datetime
    print("✅ datetime imported")
    
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Current directory: {os.getcwd()}")
    print(f"✅ Current time: {datetime.datetime.now()}")
    
    # List files in current directory
    files = os.listdir('.')
    print(f"✅ Files in directory: {files}")
    
    # Check if src directory exists
    if os.path.exists('src'):
        print("✅ src directory exists")
        src_files = os.listdir('src')
        print(f"✅ src directory contents: {src_files}")
    else:
        print("❌ src directory does not exist")
    
    print("✅ Minimal test completed successfully!")
    
except Exception as e:
    print(f"❌ Minimal test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 