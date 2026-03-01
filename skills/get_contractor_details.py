import urllib.request
import urllib.parse
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# From the search snippets, we identified these key contractors:
contractors = [
    'Elegant Tile and Hardwood Floors Vancouver WA',
    'Reliable Men Construction Vancouver WA',
    'NW Tub and Shower Vancouver WA',
    'TGR General Construction Vancouver WA',
    'RTA Construction Vancouver WA bathroom',
    'EcoCraft LLC Vancouver WA bathroom',
    'Becker Custom Construction Vancouver WA',
]

for c in contractors:
    print(f'\n=== Searching: {c} ===')
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(c + " phone reviews rating")}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'  Search failed: {html}')
        continue
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    
    shown = 0
    for i, (link, title) in enumerate(results[:5]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:250] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url:
            link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link:
            continue
        print(f'  {title_clean}')
        print(f'  URL: {link}')
        print(f'  Info: {snip}')
        shown += 1
        if shown >= 3:
            break
