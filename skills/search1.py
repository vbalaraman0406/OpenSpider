import urllib.request
import urllib.parse
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'top bathroom tile contractors Vancouver Washington reviews',
    'bathroom vanity installation contractors Vancouver WA',
    'bathroom remodel contractors Vancouver WA 98662 site:thumbtack.com',
     'bathroom remodel contractors Vancouver WA 98662 site:bbb.org',
     'bathroom renovation contractors Vancouver WA ratings'
]

all_text = []
for q in queries:
    url = 'https://www.google.com/search?q=' + urllib.parse.quote(q) + '&num=20&gl=us&hl=en'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Strip tags
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        all_text.append(text)
    except Exception as e:
        all_text.append(f'ERROR: {e}')

# Now extract contractor-related segments
full = ' '.join(all_text)

# Find segments mentioning ratings, stars, reviews, contractor names
patterns = [
    r'([A-Z][A-Za-z&\' ]{3,40}(?:LLC|Inc|Co|Construction|Remodel|Renovation|Tile|Bath|Plumbing|Home|Kitchen|Design|Services|Improvement|Contracting|Builders|Works)[A-Za-z. ]{0,20})',
    r'(\d\.\d)\s*(?:star|rating|out of)',
    r'(\d+)\s*reviews?',
    r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}',
    r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
]

# Extract all phone numbers
phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]+\d{3}[\-\.\s]+\d{4}', full)
print('=== PHONES ===')
for p in set(phones):
    print(p)

# Extract company-like names near keywords
segments = re.findall(r'.{0,80}(?:contractor|remodel|tile|vanity|bath|renovation|plumb|rating|review|star|\d\.\d).{0,80}', full, re.IGNORECASE)
print('\n=== RELEVANT SEGMENTS ===')
seen = set()
for s in segments[:100]:
    s = s.strip()
    if len(s) > 20 and s not in seen:
        seen.add(s)
        print(s)
        print('---')
