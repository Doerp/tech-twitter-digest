#!/usr/bin/env python3
"""
Test script to debug what's failing
"""
import sys
print("Python version:", sys.version)
print("Starting imports...")

try:
    print("1. Importing requests...", end=" ")
    import requests
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("2. Importing BeautifulSoup...", end=" ")
    from bs4 import BeautifulSoup
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("3. Importing feedgen...", end=" ")
    import feedgen.feed
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

try:
    print("4. Importing datetime...", end=" ")
    from datetime import datetime, timedelta
    print("✓")
except Exception as e:
    print(f"✗ {e}")
    sys.exit(1)

print("\nAll imports successful!")
print("\nTesting file creation...")

try:
    with open('test_file.txt', 'w') as f:
        f.write('test')
    print("✓ Can create files")
    
    import os
    if os.path.exists('test_file.txt'):
        print("✓ File exists")
        os.remove('test_file.txt')
    else:
        print("✗ File not found after creation")
except Exception as e:
    print(f"✗ Cannot create files: {e}")

print("\nTesting feedgen...")
try:
    fg = feedgen.feed.FeedGenerator()
    fg.id('test')
    fg.title('Test Feed')
    fg.link(href='http://example.com', rel='alternate')
    fg.rss_file('test_feed.xml')
    
    import os
    if os.path.exists('test_feed.xml'):
        print("✓ RSS file created successfully")
        print(f"  File size: {os.path.getsize('test_feed.xml')} bytes")
        os.remove('test_feed.xml')
    else:
        print("✗ RSS file not created")
except Exception as e:
    print(f"✗ Error creating RSS: {e}")
    import traceback
    traceback.print_exc()

print("\n=== All tests passed! ===")
