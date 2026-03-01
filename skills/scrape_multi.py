import urllib.request
import re
import json

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    resp = urllib.request.urlopen(req, timeout=15)
    return resp.read().decode('utf-8', errors='ignore')

# Try Houzz
try:
    print('=== HOUZZ ===')
    html = fetch('https://www.houzz.com/professionals/general-contractor/bathroom-remodel/vancouver-wa-us')
    names = re.findall(r'"displayName":"([^"]+)"', html)
    for n in names[:10]:
        print(f'  - {n}')
    if not names:
        print('No names found via JSON. Trying alt pattern...')
        names2 = re.findall(r'class="hz-pro-search-result__name"[^>]*>([^<]+)<', html)
        for n in names2[:10]:
            print(f'  - {n}')
except Exception as e:
    print(f'Houzz error: {e}')

# Try Google Maps / Places-like search via DuckDuckGo
try:
    print('\n=== DUCKDUCKGO LITE ===')
    url = 'https://lite.duckduckgo.com/lite/?q=best+rated+bathroom+remodel+contractors+Vancouver+WA+98662+reviews'
    html = fetch(url)
    # Extract result snippets
    results = re.findall(r'<a[^>]+href="([^"]+)"[^>]*class="result-link"[^>]*>([^<]+)</a>', html)
    if not results:
        results = re.findall(r'<a[^>]+rel="nofollow"[^>]+href="([^"]+)"[^>]*>\s*([^<]+)</a>', html)
    if not results:
        # Try broader pattern
        links = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*>([^<]{10,})</a>', html)
        results = links
    for url_r, title in results[:15]:
        print(f'  {title.strip()} -> {url_r}')
    if not results:
        print('No results. HTML snippet:')
        print(html[:1500])
except Exception as e:
    print(f'DDG error: {e}')

# Try BBB
try:
    print('\n=== BBB ===')
    html = fetch('https://www.bbb.org/search?find_country=US&find_loc=Vancouver%2C%20WA&find_text=bathroom%20remodel&find_type=Category&page=1')
    names = re.findall(r'"businessName":"([^"]+)"', html)
    if not names:
        names = re.findall(r'data-testid="result-name"[^>]*>([^<]+)<', html)
    for n in names[:10]:
        print(f'  - {n}')
    if not names:
        print('No BBB results found')
except Exception as e:
    print(f'BBB error: {e}')