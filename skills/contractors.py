import requests
from bs4 import BeautifulSoup
import re, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml'
}

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'bathroom tile and vanity replacement contractors Vancouver Washington reviews',
    'top bathroom renovation contractors Vancouver WA ratings',
    'bathroom remodel contractor Vancouver WA 98662 site:thumbtack.com',
    'bathroom remodel contractor Vancouver WA 98662 site:bbb.org',
    'bathroom remodel contractor Vancouver WA 98662 site:buildzoom.com'
]

all_text = []
for q in queries:
    try:
        url = f'https://www.google.com/search?q={requests.utils.quote(q)}&num=20&gl=us'
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Extract all visible text snippets
        for div in soup.find_all(['div','span','a','h3']):
            t = div.get_text(' ', strip=True)
            if t and len(t) > 20:
                all_text.append(t)
    except Exception as e:
        all_text.append(f'Error on query: {e}')

# Deduplicate
seen = set()
unique = []
for t in all_text:
    if t not in seen:
        seen.add(t)
        unique.append(t)

# Print first 8000 chars of combined text for analysis
combined = '\n'.join(unique)
print(combined[:8000])
