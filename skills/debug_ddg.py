import urllib.request
import re

url = 'https://html.duckduckgo.com/html/?q=best+rated+bathroom+remodel+contractors+Vancouver+WA+98662'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Print first 3000 chars to see structure
    print('=== FIRST 3000 CHARS ===')
    print(html[:3000])
    print('\n=== SEARCHING FOR RESULT PATTERNS ===')
    # Look for common patterns
    for pattern in ['result__', 'web-result', 'links_main', 'result-link', 'snippet', 'a href']:
        count = html.lower().count(pattern.lower())
        print(f'  Pattern "{pattern}": {count} occurrences')
    # Try to find all links
    links = re.findall(r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]+)"', html)
    print(f'\nResult links found: {len(links)}')
    for l in links[:10]:
        print(f'  {l}')
    # Try finding any href with contractor-related text
    all_links = re.findall(r'href="(https?://[^"]+)"', html)
    print(f'\nAll https links: {len(all_links)}')
    for l in all_links[:20]:
        print(f'  {l}')
except Exception as e:
    print(f'Error: {e}')
