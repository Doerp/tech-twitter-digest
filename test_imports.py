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

print("\nAll imports successful!")
print("\nTesting feedgen RSS creation...")

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
    else:
        print("✗ RSS file not created")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
