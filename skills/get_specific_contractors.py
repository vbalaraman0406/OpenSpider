import urllib.request
import urllib.parse
import re
import ssl
import time

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Search for each specific contractor
contractors = [
    'Reliable Men Construction Vancouver WA phone rating reviews',
    'Elegant Tile and Hardwood Floors Vancouver WA phone rating reviews',
    'NW Tub and Shower Vancouver WA phone rating reviews',
    'Columbia River Tile and Stone Vancouver WA phone rating reviews',
    'SingleTrack Construction Vancouver WA phone rating reviews',
    'Mr Tapia Maintenance Remodeling Vancouver WA phone rating reviews',
    'EcoCraft LLC Vancouver WA bathroom phone rating reviews',
]

for q in contractors:
    print(f'\n=== {q.split(" Vancouver")[0]} ===')
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'  Failed: {html}')
        continue
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    
    shown = 0
    for i, (link, title) in enumerate(results[:8]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url:
            link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link:
            continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        print()
        shown += 1
        if shown >= 3:
            break
    time.sleep(2)
