#!/usr/bin/env python3
import requests
import feedparser
from datetime import datetime, timedelta, timezone
import sys
import json

# RSS feed for Trump's Truth Social (example - using rss.app)
RSS_URL = "https://rss.app/feeds/truthsocial-donaldtrump.xml"

# Time threshold: last 30 minutes
NOW = datetime.now(timezone.utc)
THRESHOLD = NOW - timedelta(minutes=30)

def fetch_posts():
    """Fetch and parse RSS feed for Trump's Truth Social posts."""
    try:
        feed = feedparser.parse(RSS_URL)
        posts = []
        for entry in feed.entries:
            # Parse timestamp
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc) if hasattr(entry, 'published_parsed') else NOW
            # Extract content
            title = entry.get('title', 'No title')
            summary = entry.get('summary', 'No summary')
            link = entry.get('link', 'No link')
            posts.append({
                'timestamp': published.isoformat(),
                'published': published,
                'topic_summary': title,
                'content': summary,
                'link': link
            })
        return posts
    except Exception as e:
        print(f"Error fetching RSS feed: {e}", file=sys.stderr)
        return []

def filter_new_posts(posts):
    """Filter posts from the last 30 minutes."""
    new_posts = [p for p in posts if p['published'] >= THRESHOLD]
    return new_posts

def main():
    posts = fetch_posts()
    new_posts = filter_new_posts(posts)
    
    # Output results as JSON for further processing
    result = {
        'new_posts': [
            {
                'timestamp': p['timestamp'],
                'topic_summary': p['topic_summary'],
                'content': p['content']
            } for p in new_posts
        ],
        'count': len(new_posts),
        'threshold': THRESHOLD.isoformat()
    }
    print(json.dumps(result, indent=2))
    
    # Exit code for scripting
    if new_posts:
        sys.exit(0)  # New posts found
    else:
        sys.exit(1)  # No new posts

if __name__ == "__main__":
    main()