import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Try direct URL guesses
guesses = [
    'https://www.fazzolariconstruction.com',
    'https://www.fazzolariconstruction.com',
    'https://fazzolaricontractor.com',
    'https://www.fazzolarihomes.com',
    'https://fazzolariremodeling.com',
    'https://www.fazzolari.com',
]

for url in guesses:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=5, context=ctx)
        html = resp.read().decode('utf-8', errors='ignore')[:2000]
        title = re.search(r'<title[^>]*>(.*?)</title>', html, re.I|re.S)
        print(f'FOUND: {url}')
        if title:
            print(f'  Title: {title.group(1).strip()}')
        # Extract phone numbers
        phones = re.findall(r'[\(]?\d{3}[\)\-\.\s]?\s?\d{3}[\-\.\s]?\d{4}', html)
        if phones:
            print(f'  Phones: {phones[:3]}')
        break
    except Exception as e:
        print(f'FAIL: {url} -> {str(e)[:80]}')

# Try DuckDuckGo HTML search
print('\n--- DuckDuckGo Search ---')
try:
    q = urllib.parse.quote('Fazzolari contractor Vancouver WA')
    url = f'https://html.duckduckgo.com/html/?q={q}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract result links
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    if not results:
        results = re.findall(r'href="(https?://[^"]+)"[^>]*>(.*?)</a>', html, re.S)
    for link, text in results[:10]:
        clean_text = re.sub(r'<[^>]+>', '', text).strip()
        if 'duckduckgo' not in link.lower():
            print(f'  {clean_text[:80]} -> {link[:120]}')
except Exception as e:
    print(f'DDG Error: {e}')

# Try Yelp direct search
print('\n--- Yelp Search ---')
try:
    q = urllib.parse.quote('Fazzolari')
    url = f'https://www.yelp.com/search?find_desc={q}&find_loc=Vancouver%2C+WA'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for business names and ratings
    biz = re.findall(r'"name":"([^"]*[Ff]azzolari[^"]*)"|([Ff]azzolari[^<]{0,60})', html)
    print(f'  Yelp matches: {biz[:5]}')
    ratings = re.findall(r'"rating":(\d\.?\d?)', html)
    if ratings:
        print(f'  Ratings found: {ratings[:3]}')
    reviews = re.findall(r'"reviewCount":(\d+)', html)
    if reviews:
        print(f'  Review counts: {reviews[:3]}')
except Exception as e:
    print(f'Yelp Error: {e}')
