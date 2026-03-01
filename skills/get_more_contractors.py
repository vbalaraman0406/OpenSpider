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

# Search for more contractors and their details
additional_searches = [
    'NW Tub Shower Vancouver WA phone reviews',
    'TGR General Construction Vancouver WA phone reviews bathroom',
    'RTA Construction LLC Vancouver WA bathroom remodel reviews',
    'EcoCraft LLC Vancouver WA contractor reviews',
    'bathroom remodeling contractors Vancouver WA 98662 top rated 2024',
    'Vancouver WA tile installer bathroom remodel reviews phone number',
]

for q in additional_searches:
    print(f'\n=== {q} ===')
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
