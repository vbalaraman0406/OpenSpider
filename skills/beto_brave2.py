import requests
from bs4 import BeautifulSoup
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try multiple Brave searches to find rating info
queries = [
    'Beto+and+Son+Remodeling+LLC+Vancouver+WA+reviews+rating',
    'Beto+%26+Son+Remodeling+Vancouver+WA+google+reviews',
    'site:yelp.com+beto+son+remodeling+vancouver+wa'
]

for q in queries:
    try:
        url = f'https://search.brave.com/search?q={q}'
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Get all text snippets
        snippets = soup.find_all(['p', 'span', 'div'], string=re.compile(r'(beto|rating|review|star)', re.I))
        print(f'\n=== Query: {q} ===')
        for s in snippets[:10]:
            text = s.get_text(strip=True)[:200]
            if len(text) > 20:
                print(text)
        # Also look for links
        links = soup.find_all('a', href=re.compile(r'(yelp|google|bbb|angi|homeadvisor)', re.I))
        for l in links[:5]:
            print(f'Link: {l.get("href", "")[:150]}')
    except Exception as e:
        print(f'Error: {e}')

# Try MapQuest page directly
try:
    r = requests.get('https://www.mapquest.com/us/wa/beto-and-son-remodeling-llc-474792757', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    # Look for rating
    rating_els = soup.find_all(string=re.compile(r'\d+\.\d+.*(?:star|rating|review)', re.I))
    for el in rating_els[:5]:
        print(f'MapQuest: {el.strip()[:200]}')
    # Look for phone, address
    phone = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', soup.get_text())
    print(f'MapQuest phones: {phone[:3]}')
    # Get JSON-LD
    scripts = soup.find_all('script', type='application/ld+json')
    for s in scripts:
        data = json.loads(s.string)
        print(f'MapQuest JSON-LD: {json.dumps(data)[:500]}')
except Exception as e:
    print(f'MapQuest error: {e}')

# Try HomeYou page
try:
    r = requests.get('https://www.homeyou.com/wa/beto-and-son-remodeling-llc-vancouver', headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    text = soup.get_text()
    # Find rating patterns
    ratings = re.findall(r'(\d+\.\d+)\s*(?:out of|/|stars?|rating)', text, re.I)
    reviews = re.findall(r'(\d+)\s*(?:reviews?|ratings?)', text, re.I)
    print(f'HomeYou ratings: {ratings[:5]}')
    print(f'HomeYou reviews: {reviews[:5]}')
    # Get relevant text
    for line in text.split('\n'):
        line = line.strip()
        if 'beto' in line.lower() and len(line) > 20 and len(line) < 300:
            print(f'HomeYou: {line}')
except Exception as e:
    print(f'HomeYou error: {e}')
