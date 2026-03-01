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

# Now let me get specifics: phone numbers, ratings for the ones we've identified
# Try fetching contractor website pages directly

print('=== 1. Elegant Tile and Hardwood Floors ===')
html = fetch('https://www.chamberofcommerce.com/united-states/washington/vancouver/flooring-store/1332338272-elegant-tile-and-hardwood-floors-llc')
if not html.startswith('ERROR'):
    phones = re.findall(r'[\(]?\d{3}[\)]?[-.\s]?\d{3}[-.\s]?\d{4}', html)
    phones = list(set(phones))
    title = re.findall(r'<title>(.*?)</title>', html, re.IGNORECASE)
    print(f'  Phone(s): {phones[:3]}')
    if title: print(f'  Title: {title[0][:150]}')
else:
    print(f'  {html}')

time.sleep(3)

# Get remaining contractors
print('\n=== 2. NW Tub and Shower ===')
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote("NW Tub Shower Vancouver WA bathroom phone reviews yelp")}'
html = fetch(url)
if not html.startswith('ERROR'):
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    shown = 0
    for i, (link, title) in enumerate(results[:8]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url: link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link: continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        shown += 1
        if shown >= 2: break

time.sleep(4)

print('\n=== 3. Mr Tapia Maintenance and Remodeling ===')
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote("Mr Tapia Maintenance Remodeling Vancouver WA phone reviews")}'
html = fetch(url)
if not html.startswith('ERROR'):
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    shown = 0
    for i, (link, title) in enumerate(results[:8]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url: link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link: continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        shown += 1
        if shown >= 2: break

time.sleep(4)

print('\n=== 4. Columbia River Tile Stone ===')
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote("Columbia River Tile Stone Vancouver WA phone reviews")}'
html = fetch(url)
if not html.startswith('ERROR'):
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    shown = 0
    for i, (link, title) in enumerate(results[:8]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url: link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link: continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        shown += 1
        if shown >= 2: break

time.sleep(4)

print('\n=== 5. SingleTrack Construction ===')
url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote("SingleTrack Construction Vancouver WA bathroom phone reviews")}'
html = fetch(url)
if not html.startswith('ERROR'):
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    shown = 0
    for i, (link, title) in enumerate(results[:8]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url: link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link: continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        shown += 1
        if shown >= 2: break
