import urllib.request
import re

url = 'https://lite.duckduckgo.com/lite/?q=best+rated+bathroom+remodel+contractors+Vancouver+WA+98662+tile+vanity'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract result links and snippets
    # DDG Lite uses simple table layout
    results = re.findall(r'<a[^>]+href="(http[^"]+)"[^>]*class="result-link"[^>]*>([^<]+)</a>', html)
    if not results:
        results = re.findall(r'<a[^>]+href="(http[^"]+)"[^>]*>([^<]+)</a>', html)
    snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html, re.DOTALL)
    if not snippets:
        snippets = re.findall(r'<span[^>]*class="link-text"[^>]*>(.*?)</span>', html, re.DOTALL)
    
    print(f'Found {len(results)} links')
    for i, (link, title) in enumerate(results[:20]):
        if 'duckduckgo' not in link:
            snip = snippets[i].strip() if i < len(snippets) else ''
            snip = re.sub(r'<[^>]+>', '', snip)[:200]
            print(f'\nTitle: {title.strip()}')
            print(f'URL: {link}')
            print(f'Snippet: {snip}')
except Exception as e:
    print(f'Error: {e}')
    # Try saving raw HTML for debug
    try:
        with open('ddg_raw.html', 'w') as f:
            f.write(html)
        print('Saved raw HTML to ddg_raw.html')
    except:
        pass
