import requests
from html.parser import HTMLParser
import re

class TitleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = []
        self.in_title = False
        self.current = ''
        self.capture_tags = set()
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        # For The Hacker News
        if 'home-title' in cls or 'story-title' in cls:
            self.in_title = True
            self.current = ''
        # For generic h2/h3 article titles
        if tag in ('h2', 'h3') and any(k in cls for k in ['title', 'heading', 'entry', 'article', 'post']):
            self.in_title = True
            self.current = ''
    def handle_data(self, data):
        if self.in_title:
            self.current += data.strip() + ' '
    def handle_endtag(self, tag):
        if self.in_title and tag in ('a', 'h2', 'h3', 'div', 'span'):
            if self.current.strip() and len(self.current.strip()) > 15:
                self.titles.append(self.current.strip())
            self.in_title = False
            self.current = ''

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

sources = {
    'The Hacker News': 'https://thehackernews.com/',
    'BleepingComputer': 'https://www.bleepingcomputer.com/',
    'SecurityWeek': 'https://www.securityweek.com/',
    'The Record': 'https://therecord.media/',
    'Dark Reading': 'https://www.darkreading.com/',
}

for name, url in sources.items():
    print(f'\n=== {name} ===')
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # Extract all text between h2/h3 tags with links
        # Simple regex approach
        headlines = re.findall(r'<h[23][^>]*>\s*(?:<a[^>]*>)?\s*([^<]{20,}?)\s*(?:</a>)?\s*</h[23]>', r.text)
        if not headlines:
            # Try broader pattern
            headlines = re.findall(r'<a[^>]*>\s*<h[23][^>]*>([^<]{20,}?)</h[23]>', r.text)
        if not headlines:
            headlines = re.findall(r'title["\']?[^>]*>([^<]{25,}?)</', r.text)[:20]
        seen = set()
        count = 0
        for h in headlines:
            h = h.strip()
            if h not in seen and len(h) > 20 and count < 15:
                seen.add(h)
                print(f'  - {h}')
                count += 1
        if count == 0:
            print('  (No headlines extracted)')
    except Exception as e:
        print(f'  Error: {e}')
