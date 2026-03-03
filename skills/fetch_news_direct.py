import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5'
}

# Try multiple news sources directly
sources = [
    ('Reuters Iran', 'https://www.reuters.com/world/middle-east/'),
    ('AP News', 'https://apnews.com/hub/iran'),
    ('BBC Middle East', 'https://www.bbc.com/news/world/middle_east'),
    ('Al Jazeera', 'https://www.aljazeera.com/where/iran/'),
]

for name, url in sources:
    print(f'\n=== {name} ===')
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Find all links with text that might be headlines
        headlines = []
        for a in soup.find_all('a'):
            text = a.get_text(strip=True)
            href = a.get('href', '')
            # Filter for Iran-related or conflict-related headlines
            if len(text) > 30 and len(text) < 200:
                text_lower = text.lower()
                if any(kw in text_lower for kw in ['iran', 'tehran', 'strike', 'military', 'war', 'conflict', 'nuclear', 'missile', 'sanction', 'tension', 'irgc', 'houthi', 'hezbollah']):
                    if text not in [h['title'] for h in headlines]:
                        full_url = href if href.startswith('http') else (url.rstrip('/') + href if href.startswith('/') else '')
                        headlines.append({'title': text, 'url': full_url})
        for h in headlines[:5]:
            print(f"  - {h['title']}")
            print(f"    {h['url']}")
        if not headlines:
            # Print any headlines as fallback
            all_h = []
            for tag in soup.find_all(['h2','h3','h4']):
                t = tag.get_text(strip=True)
                if len(t) > 20 and len(t) < 200:
                    all_h.append(t)
            print(f'  No Iran-specific headlines. Top headlines:')
            for h in all_h[:5]:
                print(f'  - {h}')
    except Exception as e:
        print(f'  Error: {e}')

# Also try Google News RSS
print('\n=== Google News RSS ===')
try:
    rss_url = 'https://news.google.com/rss/search?q=Iran+war+conflict&hl=en-US&gl=US&ceid=US:en'
    resp = requests.get(rss_url, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, 'xml')
    items = soup.find_all('item')[:10]
    for item in items:
        title = item.find('title').get_text() if item.find('title') else ''
        pub = item.find('pubDate').get_text() if item.find('pubDate') else ''
        link = item.find('link').get_text() if item.find('link') else ''
        print(f'  - [{pub}] {title}')
        print(f'    {link}')
except Exception as e:
    print(f'  Error: {e}')
