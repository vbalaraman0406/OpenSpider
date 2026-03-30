import requests
import warnings
warnings.filterwarnings('ignore')
from html.parser import HTMLParser
import re

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'header', 'footer'):
            self.skip = True
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'header', 'footer'):
            self.skip = False
    def handle_data(self, data):
        if not self.skip:
            t = data.strip()
            if len(t) > 20:
                self.text.append(t)

urls = [
    'https://www.bbc.com/news/articles/c5y615v6v1zo',
    'https://www.npr.org/2026/03/15/iran-foreign-minister-ceasefire',
    'https://www.dw.com/en/iran-war-trump-says-peace-deal-terms-not-good-enough-yet/a-72345678',
]

# Try to read Al Jazeera live updates
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

# Let's try reading Al Jazeera's live blog
try:
    print('=== AL JAZEERA LIVE UPDATES ===')
    resp = requests.get('https://www.aljazeera.com/news/liveblog/2026/3/15/iran-war-live', headers=headers, timeout=15, verify=False)
    parser = TextExtractor()
    parser.feed(resp.text)
    text = '\n'.join(parser.text[:30])
    print(text[:2000])
except Exception as e:
    print(f'AJ Error: {e}')

print('\n\n=== BBC ARTICLE ===')
try:
    resp = requests.get('https://www.bbc.com/news/world-middle-east', headers=headers, timeout=15, verify=False)
    parser = TextExtractor()
    parser.feed(resp.text)
    # Find Iran-related content
    for t in parser.text:
        if 'iran' in t.lower() or 'hormuz' in t.lower() or 'tehran' in t.lower():
            print(t)
except Exception as e:
    print(f'BBC Error: {e}')

print('\n\n=== REUTERS ===')
try:
    resp = requests.get('https://www.reuters.com/world/middle-east/', headers=headers, timeout=15, verify=False)
    parser = TextExtractor()
    parser.feed(resp.text)
    for t in parser.text:
        if 'iran' in t.lower() or 'hormuz' in t.lower() or 'trump' in t.lower():
            print(t)
except Exception as e:
    print(f'Reuters Error: {e}')
