import urllib.request
import re
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts = []
    def handle_data(self, data):
        self.texts.append(data.strip())
    def get_text(self):
        return ' '.join(t for t in self.texts if t)

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.read().decode('utf-8','ignore')
    except:
        return ''

# Search for phone numbers and ratings for each contractor
contractors = [
    'Elegant Tile and Hardwood Floors Vancouver WA',
    'Reliable Men Construction Vancouver WA',
    'NW Tub and Shower Vancouver WA',
    'Affordable Contractor Services Vancouver WA',
    'Allcraft Home Vancouver WA',
]

for c in contractors:
    q = c.replace(' ','+')
    url = f'https://html.duckduckgo.com/html/?q={q}+phone+number+rating+reviews'
    html = fetch(url)
    p = TextExtractor()
    p.feed(html)
    text = p.get_text()
    # Find phone numbers
    phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    # Find ratings like 4.8, 5.0 etc near words like star/rating
    ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|out of)', text, re.I)
    # Find review counts
    reviews = re.findall(r'(\d+)\s*(?:review|reviews)', text, re.I)
    print(f'=== {c} ===')
    print(f'Phones: {phones[:3]}')
    print(f'Ratings: {ratings[:3]}')
    print(f'Reviews: {reviews[:3]}')
    # Print first 500 chars for context
    print(f'Snippet: {text[:400]}')
    print()
