#!/usr/bin/env python3
"""
Very simple test for GitHub Actions.
"""

print("🚀 Simple test starting...")

try:
    import os
    print("✅ os imported")
    
    import sys
    print("✅ sys imported")
    
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Current directory: {os.getcwd()}")
    print(f"✅ Files in directory: {os.listdir('.')}")
    
    # Try to import our modules
    try:
        import src
        print("✅ src module imported")
    except Exception as e:
        print(f"❌ src import failed: {e}")
        
    print("✅ Simple test completed successfully!")
    
except Exception as e:
    print(f"❌ Simple test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1) 