import urllib.request
import re

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def clean_html(html):
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# Scrape key business websites
sites = [
    ('All Brothers Contracting', 'https://www.allbroscontracting.com/'),
    ('Re-Bath Portland', 'https://www.rebath.com/location/portland/'),
    ('Neil Kelly Company', 'https://www.neilkelly.com/'),
    ('Rapid Bath NW / Alta Casa NW', 'https://www.rapidbathnw.com/'),
    ('Cascade NW Plumbing', 'https://www.cascadenorthwestplumbing.com/bathroom-remodeling-services/'),
    ('Pacific Bath', 'https://pacific-bath.com/'),
    ('Bath Pros NW', 'https://www.bathprosnw.com/'),
    ('Tile Craft LLC', 'https://www.buildzoom.com/contractor/tile-craft-llc-vancouver-wa'),
]

for name, url in sites:
    try:
        html = fetch(url)
        text = clean_html(html)
        # Get phone numbers
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        phones = list(dict.fromkeys(phones))[:3]
        # Get title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.DOTALL)
        title = title_match.group(1).strip() if title_match else 'N/A'
        title = re.sub(r'<[^>]+>', '', title)[:100]
        # Look for service keywords
        services = []
        for kw in ['tile', 'floor', 'wall', 'vanity', 'bathroom', 'remodel', 'shower', 'tub', 'counter', 'cabinet']:
            if kw.lower() in text.lower():
                services.append(kw)
        # Look for location keywords
        locations = []
        for loc in ['Vancouver', 'Orchards', 'Clark County', 'Portland']:
            if loc.lower() in text.lower():
                locations.append(loc)
        
        print(f'=== {name} ===')
        print(f'  Title: {title}')
        print(f'  URL: {url}')
        if phones: print(f'  Phone: {phones}')
        print(f'  Services mentioned: {services}')
        print(f'  Locations: {locations}')
        # Extract a short snippet about services (first 200 chars mentioning tile/bathroom)
        idx = text.lower().find('tile')
        if idx > 0:
            snippet = text[max(0,idx-50):idx+150].strip()
            print(f'  Snippet: {snippet[:200]}')
        print()
    except Exception as e:
        print(f'=== {name} === ERROR: {e}\n')

# Also scrape Yelp page for All Brothers
try:
    html = fetch('https://www.yelp.com/biz/all-brothers-contracting-vancouver')
    text = clean_html(html)
    # Find rating
    rating = re.findall(r'(\d+\.\d+)\s*star', text, re.I)
    reviews = re.findall(r'(\d+)\s*review', text, re.I)
    phone = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    print('=== Yelp: All Brothers ===')
    if rating: print(f'  Rating: {rating[:2]}')
    if reviews: print(f'  Reviews: {reviews[:2]}')
    if phone: print(f'  Phone: {list(dict.fromkeys(phone))[:2]}')
except Exception as e:
    print(f'Yelp error: {e}')
