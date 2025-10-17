import requests
from bs4 import BeautifulSoup
import feedgen.feed
from datetime import datetime, timedelta, timezone
import time
import random
import json
import os

class TwitterListRSSGenerator:
    def __init__(self):
        # Public Nitter instances (rotate if one fails)
        self.nitter_instances = [
            'https://nitter.poast.org',
            'https://nitter.net',
            'https://nitter.privacydev.net',
            'https://nitter.unixfox.eu',
            'https://nitter.mint.lgbt'
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Cache file for list members
        self.cache_file = 'list_members_cache.json'
        self.accounts = []
    
    def get_working_instance(self):
        """Find a working Nitter instance"""
        for instance in self.nitter_instances:
            try:
                response = self.session.get(instance, timeout=10)
                if response.status_code == 200:
                    print(f"Using Nitter instance: {instance}")
                    return instance
            except:
                continue
        return self.nitter_instances[0]  # Fallback
    
    def fetch_list_members(self, list_url, instance_url):
        """Fetch members from a Twitter list via Nitter"""
        try:
            # Convert Twitter list URL to Nitter format
            # https://x.com/i/lists/1539497752140206080 -> https://nitter.net/i/lists/1539497752140206080
            list_id = list_url.split('/lists/')[-1].strip()
            nitter_url = f"{instance_url}/i/lists/{list_id}"
            
            print(f"Fetching list members from: {nitter_url}")
            response = self.session.get(nitter_url, timeout=15)
            
            if response.status_code != 200:
                print(f"Failed to fetch list (status {response.status_code})")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            members = []
            
            # Find all user links in the list
            user_links = soup.find_all('a', class_='username')
            
            for link in user_links:
                username = link.get_text(strip=True).replace('@', '')
                if username and username not in members:
                    members.append(username)
            
            print(f"Found {len(members)} members in list")
            return members
            
        except Exception as e:
            print(f"Error fetching list members: {e}")
            return []
    
    def load_cached_members(self):
        """Load cached list members if available"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded {len(data['accounts'])} accounts from cache")
                    return data['accounts']
            except:
                pass
        return []
    
    def save_cached_members(self, accounts):
        """Save list members to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'accounts': accounts,
                    'updated_at': datetime.now().isoformat()
                }, f, indent=2)
            print(f"Cached {len(accounts)} accounts")
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def fetch_all_list_members(self, list_urls):
        """Fetch members from all provided lists"""
        instance = self.get_working_instance()
        all_members = set()
        
        for list_url in list_urls:
            print(f"\nProcessing list: {list_url}")
            members = self.fetch_list_members(list_url, instance)
            all_members.update(members)
            time.sleep(random.uniform(2, 4))  # Be polite
        
        return list(all_members)
    
    def fetch_tweets_from_account(self, username, instance_url, max_tweets=3):
        """Fetch recent tweets from a user via Nitter"""
        try:
            url = f"{instance_url}/{username}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            tweets = []
            
            # Find all tweet containers
            tweet_items = soup.find_all('div', class_='timeline-item')[:max_tweets]
            
            for item in tweet_items:
                try:
                    # Skip retweets
                    if item.find('div', class_='retweet-header'):
                        continue
                    
                    # Extract tweet content
                    content_div = item.find('div', class_='tweet-content')
                    if not content_div:
                        continue
                    
                    text = content_div.get_text(strip=True)
                    
                    # Skip if too short (likely just a link)
                    if len(text) < 20:
                        continue
                    
                    # Extract tweet link
                    link_elem = item.find('a', class_='tweet-link')
                    if link_elem:
                        tweet_path = link_elem.get('href', '')
                        tweet_url = f"https://twitter.com{tweet_path}"
                    else:
                        continue
                    
                    # Extract stats
                    stats = item.find('div', class_='tweet-stats')
                    likes = 0
                    retweets = 0
                    replies = 0
                    
                    if stats:
                        stat_spans = stats.find_all('span', class_='tweet-stat')
                        for span in stat_spans:
                            icon = span.find('span', class_='icon')
                            num_span = span.find('span', class_='icon-text')
                            
                            if icon and num_span:
                                icon_class = icon.get('class', [])
                                try:
                                    num = int(num_span.get_text(strip=True).replace(',', ''))
                                except:
                                    num = 0
                                
                                if 'icon-retweet' in icon_class:
                                    retweets = num
                                elif 'icon-heart' in icon_class:
                                    likes = num
                                elif 'icon-comment' in icon_class:
                                    replies = num
                    
                    # Extract timestamp
                    date_elem = item.find('span', class_='tweet-date')
                    created_at = datetime.now()
                    
                    if date_elem:
                        date_link = date_elem.find('a')
                        if date_link and date_link.get('title'):
                            try:
                                date_str = date_link['title']
                                created_at = datetime.strptime(date_str, '%b %d, %Y · %I:%M %p UTC')
                            except:
                                pass
                    
                    # Only include tweets from last 24 hours
                    if (datetime.now() - created_at).days > 1:
                        continue
                    
                    tweets.append({
                        'author': username,
                        'text': text,
                        'url': tweet_url,
                        'likes': likes,
                        'retweets': retweets,
                        'replies': replies,
                        'created_at': created_at,
                        'engagement': likes + (retweets * 2) + replies  # Weight retweets more
                    })
                    
                except Exception as e:
                    continue
            
            return tweets
            
        except Exception as e:
            print(f"Error fetching from @{username}: {e}")
            return []
    
    def fetch_all_tweets(self):
        """Fetch tweets from all monitored accounts"""
        if not self.accounts:
            print("No accounts to fetch from!")
            return []
        
        instance = self.get_working_instance()
        all_tweets = []
        
        print(f"\nFetching tweets from {len(self.accounts)} accounts...")
        
        for i, username in enumerate(self.accounts):
            print(f"[{i+1}/{len(self.accounts)}] @{username}...", end=' ')
            
            tweets = self.fetch_tweets_from_account(username, instance, max_tweets=3)
            
            if tweets:
                all_tweets.extend(tweets)
                print(f"✓ {len(tweets)} tweets")
            else:
                print("✗")
            
            # Be polite - add delay
            if i < len(self.accounts) - 1:
                time.sleep(random.uniform(1, 2))
        
        # Sort by engagement
        all_tweets.sort(key=lambda x: x['engagement'], reverse=True)
        
        print(f"\nTotal tweets collected: {len(all_tweets)}")
        return all_tweets[:100]  # Top 100 most engaging tweets
    
    def generate_rss(self, tweets, output_file='tech_ai_twitter.xml'):
        """Generate RSS feed from tweets"""
        fg = feedgen.feed.FeedGenerator()
        fg.id('https://yourdomain.com/tech-ai-twitter')
        fg.title('Tech & AI Twitter Daily Digest')
        fg.author({'name': 'Twitter List Aggregator'})
        fg.link(href='https://yourdomain.com/tech-ai-twitter', rel='alternate')
        fg.subtitle('Daily highlights from curated Twitter lists')
        fg.language('en')
        fg.updated(datetime.now())
        
        for tweet in tweets:
            fe = fg.add_entry()
            fe.id(tweet['url'])
            
            # Create title with preview
            title_text = tweet['text'][:120]
            if len(tweet['text']) > 120:
                title_text += '...'
            fe.title(f"@{tweet['author']}: {title_text}")
            
            fe.link(href=tweet['url'])
            
            # Create description with full text and stats
            description = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
                <p style="font-size: 15px; line-height: 1.5; margin: 0 0 12px 0;">{tweet['text']}</p>
                <p style="color: #536471; font-size: 14px; margin: 0;">
                    <strong>@{tweet['author']}</strong> · 
                    👍 {tweet['likes']:,} · 
                    🔄 {tweet['retweets']:,} · 
                    💬 {tweet['replies']:,}
                </p>
                <p style="margin-top: 12px;">
                    <a href="{tweet['url']}" style="color: #1d9bf0; text-decoration: none;">View on Twitter →</a>
                </p>
            </div>
            """
            fe.description(description)
            fe.published(tweet['created_at'])
        
        # Generate RSS file
        fg.rss_file(output_file)
        print(f"\n✓ RSS feed generated: {output_file}")
        print(f"  Contains {len(tweets)} tweets")
        return output_file

def main():
    print("=" * 70)
    print("Tech & AI Twitter RSS Generator")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    try:
        generator = TwitterListRSSGenerator()
        
        # Your Twitter lists
        list_urls = [
            'https://x.com/i/lists/1539497752140206080',
            # Add more list URLs here if needed
        ]
        
        print(f"Lists to process: {len(list_urls)}")
        for url in list_urls:
            print(f"  - {url}")
        print()
        
        # Try to load cached members first
        cached_accounts = generator.load_cached_members()
        
        # Refresh list members every 7 days or if cache is empty
        cache_age_days = 999
        if os.path.exists(generator.cache_file):
            try:
                cache_mtime = os.path.getmtime(generator.cache_file)
                cache_age_days = (time.time() - cache_mtime) / 86400
                print(f"Cache file age: {cache_age_days:.1f} days")
            except Exception as e:
                print(f"Error checking cache age: {e}")
        
        if cached_accounts and cache_age_days < 7:
            print(f"Using cached list members (cache age: {cache_age_days:.1f} days)")
            generator.accounts = cached_accounts
        else:
            print("Fetching fresh list members...")
            generator.accounts = generator.fetch_all_list_members(list_urls)
            if generator.accounts:
                generator.save_cached_members(generator.accounts)
            else:
                print("Failed to fetch list members, trying cache...")
                generator.accounts = cached_accounts
        
        if not generator.accounts:
            print("\n❌ ERROR: No accounts found!")
            print("Creating empty RSS feed as fallback...")
            generator.generate_rss([], output_file='tech_ai_twitter.xml')
            print("Empty feed created at: tech_ai_twitter.xml")
            return
        
        print(f"\n✓ Monitoring {len(generator.accounts)} accounts")
        
        # Fetch tweets
        print("\nFetching tweets...")
        tweets = generator.fetch_all_tweets()
        
        # Generate RSS
        print(f"\nGenerating RSS feed...")
        if tweets:
            generator.generate_rss(tweets)
            print(f"✓ Done! RSS feed ready with {len(tweets)} tweets.")
        else:
            print("⚠️  No tweets fetched. Generating empty RSS feed...")
            generator.generate_rss([], output_file='tech_ai_twitter.xml')
            print("Created empty RSS feed as placeholder.")
        
        # Verify file was created
        if os.path.exists('tech_ai_twitter.xml'):
            file_size = os.path.getsize('tech_ai_twitter.xml')
            print(f"\n✓ RSS file exists: tech_ai_twitter.xml ({file_size} bytes)")
        else:
            print("\n❌ ERROR: RSS file was not created!")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        
        # Create emergency empty RSS feed
        print("\nCreating emergency RSS feed...")
        try:
            from feedgen.feed import FeedGenerator
            fg = FeedGenerator()
            fg.id('https://yourdomain.com/tech-ai-twitter')
            fg.title('Tech & AI Twitter Daily Digest')
            fg.author({'name': 'Twitter List Aggregator'})
            fg.link(href='https://yourdomain.com/tech-ai-twitter', rel='alternate')
            fg.subtitle('Error generating feed - see logs')
            fg.language('en')
            fg.updated(datetime.now())
            fg.rss_file('tech_ai_twitter.xml')
            print("✓ Emergency RSS feed created")
        except Exception as e2:
            print(f"❌ Could not create emergency feed: {e2}")
        
        raise
