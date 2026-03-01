import urllib.request
import urllib.parse
import re

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def extract_phones(text):
    phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]+\d{3}[\-\.\s]+\d{4}', text)
    return list(set(phones))[:2]

def clean_html(html):
    text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
    return re.sub(r'<[^>]+>', ' ', text)

def scrape(url):
    try:
        html = fetch(url)
        clean = re.sub(r'\s+', ' ', clean_html(html)).strip()
        phones = extract_phones(clean)
        lower = clean.lower()
        svcs = [k for k in ['floor tile','wall tile','tile installation','tile replacement','vanity','bathroom remodel','bathroom renovation','shower tile','countertop'] if k in lower]
        ratings = re.findall(r'"ratingValue"\s*:\s*"?([\d\.]+)"?', html)
        reviews = re.findall(r'"reviewCount"\s*:\s*"?(\d+)"?', html)
        title = re.findall(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        t = re.sub(r'<[^>]+>', '', title[0]).strip()[:100] if title else ''
        return {'phones': phones, 'services': svcs, 'rating': ratings[0] if ratings else None, 'reviews': reviews[0] if reviews else None, 'title': t}
    except Exception as e:
        return {'error': str(e)}

# Scrape remaining sites that were truncated
remaining = [
    ('https://www.vantatileflooring.com/', 'Vanta Tile Flooring'),
    ('https://vancouverbaths.com/get-vanity-replacement', 'Vancouver Baths'),
    ('https://www.allbroscontracting.com/', 'All Bros Contracting'),
]

for url, label in remaining:
    info = scrape(url)
    print(f'{label} | {url}')
    print(f'  {info}')

# Now search for Yelp ratings
print('\n=== YELP SEARCH ===')
try:
    data = urllib.parse.urlencode({'q': 'site:yelp.com bathroom remodeling contractors Vancouver WA'}).encode('utf-8')
    req = urllib.request.Request('https://lite.duckduckgo.com/lite/', data=data, headers={
        'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    links = re.findall(r'href="(https?://[^"]+yelp[^"]+)"', html)
    for l in links[:10]:
        print(f'  {l[:200]}')
except Exception as e:
    print(f'Error: {e}')

# Search for Google Maps / BBB ratings
print('\n=== BBB/RATINGS SEARCH ===')
try:
    data = urllib.parse.urlencode({'q': 'bathroom remodeling Vancouver WA Orchards rating reviews BBB'}).encode('utf-8')
    req = urllib.request.Request('https://lite.duckduckgo.com/lite/', data=data, headers={
        'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    clean = re.sub(r'\s+', ' ', clean_html(html))
    # Extract snippet blocks
    snippets = re.findall(r'class="result-snippet">(.*?)<', html)
    links = re.findall(r'href="(https?://(?:www\.bbb|www\.angi|www\.homeadvisor|www\.thumbtack)[^"]+)"', html)
    for s in snippets[:5]:
        print(f'  Snippet: {s[:200]}')
    for l in links[:5]:
        print(f'  Link: {l[:200]}')
except Exception as e:
    print(f'Error: {e}')
