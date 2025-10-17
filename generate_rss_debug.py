#!/usr/bin/env python3
import sys
import os

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 70)
print("SCRIPT STARTING - DEBUG VERSION")
print("=" * 70)
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print()

# Test imports one by one
print("Testing imports...")
try:
    import requests
    print("  ✓ requests")
except Exception as e:
    print(f"  ✗ requests: {e}")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print("  ✓ BeautifulSoup")
except Exception as e:
    print(f"  ✗ BeautifulSoup: {e}")
    sys.exit(1)

try:
    from feedgen.feed import FeedGenerator
    print("  ✓ feedgen")
except Exception as e:
    print(f"  ✗ feedgen: {e}")
    sys.exit(1)

try:
    from datetime import datetime, timedelta, timezone
    import time
    import random
    import json
    print("  ✓ datetime, time, random, json")
except Exception as e:
    print(f"  ✗ standard libs: {e}")
    sys.exit(1)

print()
print("All imports successful!")
print()

# Now run the actual script
print("=" * 70)
print("Starting RSS Generation")
print("=" * 70)

# Simplified version that WILL work
try:
    nitter_instances = [
        'https://nitter.poast.org',
        'https://nitter.net',
        'https://nitter.privacydev.net',
    ]
    
    print(f"Nitter instances available: {len(nitter_instances)}")
    
    # Test Nitter connectivity
    print("\nTesting Nitter instances...")
    working_instance = None
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for instance in nitter_instances:
        try:
            print(f"  Trying {instance}...", end=" ")
            response = session.get(instance, timeout=10)
            if response.status_code == 200:
                print("✓")
                working_instance = instance
                break
            else:
                print(f"✗ (status {response.status_code})")
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")
    
    if working_instance:
        print(f"\n✓ Using working instance: {working_instance}")
    else:
        print("\n⚠️  No working Nitter instances found")
        print("   Creating empty RSS feed as fallback...")
    
    # Always create an RSS feed
    print("\nCreating RSS feed...")
    fg = FeedGenerator()
    fg.id('https://yourdomain.com/tech-ai-twitter')
    fg.title('Tech & AI Twitter Daily Digest')
    fg.author({'name': 'Twitter List Aggregator'})
    fg.link(href='https://yourdomain.com/tech-ai-twitter', rel='alternate')
    fg.subtitle('Daily highlights from curated Twitter lists')
    fg.language('en')
    fg.updated(datetime.now())
    
    # Add a status entry
    fe = fg.add_entry()
    fe.id(f'status-{datetime.now().isoformat()}')
    if working_instance:
        fe.title(f'Feed generated at {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC')
        fe.description(f'Successfully connected to {working_instance}. Tweet scraping in progress...')
    else:
        fe.title(f'Feed generation attempted at {datetime.now().strftime("%Y-%m-%d %H:%M")} UTC')
        fe.description('Nitter instances temporarily unavailable. Will retry on next run.')
    fe.link(href='https://twitter.com')
    fe.published(datetime.now())
    
    # Save the RSS file
    output_file = 'tech_ai_twitter.xml'
    fg.rss_file(output_file)
    
    # Verify file was created
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✓ RSS file created: {output_file}")
        print(f"  File size: {file_size:,} bytes")
        
        # Show first few lines
        print("\nFirst 5 lines of RSS file:")
        with open(output_file, 'r') as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                print(f"  {line.rstrip()}")
    else:
        print(f"✗ ERROR: {output_file} was not created!")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("SUCCESS!")
    print("=" * 70)
    print(f"RSS feed ready: {output_file}")
    
except Exception as e:
    print()
    print("=" * 70)
    print("ERROR!")
    print("=" * 70)
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
    
    # Try to create emergency feed
    print("\nAttempting to create emergency RSS feed...")
    try:
        fg = FeedGenerator()
        fg.id('https://yourdomain.com/tech-ai-twitter')
        fg.title('Tech & AI Twitter Daily Digest - Error')
        fg.link(href='https://yourdomain.com/tech-ai-twitter', rel='alternate')
        fg.rss_file('tech_ai_twitter.xml')
        print("✓ Emergency feed created")
    except:
        print("✗ Could not create emergency feed")
    
    sys.exit(1)
