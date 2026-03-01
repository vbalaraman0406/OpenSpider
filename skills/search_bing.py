import urllib.request
import urllib.parse
import re
import html

queries = [
    'bathroom remodel contractor Vancouver WA 98662 reviews',
    'best bathroom tile contractor Vancouver WA rated',
    'bathroom vanity replacement contractor Vancouver Washington',
    'BBB bathroom remodel contractor Vancouver WA',
    'houzz bathroom remodel Vancouver WA'
]

contractors = []

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
            # Extract result snippets
            results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</div>', raw, re.DOTALL)
            print(f'\n=== Query: {q} === ({len(results)} results)')
            for link, title, snippet in results[:8]:
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                snippet_clean = re.sub(r'<[^>]+>', '', snippet).strip()
                snippet_clean = html.unescape(snippet_clean)
                title_clean = html.unescape(title_clean)
                print(f'  Title: {title_clean}')
                print(f'  URL: {link}')
                print(f'  Snippet: {snippet_clean[:300]}')
                print()
    except Exception as e:
        print(f'Error for query "{q}": {e}')

# Also try Bing
print('\n\n=== BING SEARCH ===')
for q in queries[:3]:
    url = f'https://www.bing.com/search?q={urllib.parse.quote(q)}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
            # Bing results
            results = re.findall(r'<li class="b_algo">(.*?)</li>', raw, re.DOTALL)
            print(f'\n=== Bing: {q} === ({len(results)} results)')
            for r in results[:6]:
                title_m = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r)
                snippet_m = re.search(r'<p[^>]*>(.*?)</p>', r, re.DOTALL)
                if title_m:
                    t = re.sub(r'<[^>]+>', '', title_m.group(2)).strip()
                    u = title_m.group(1)
                    s = ''
                    if snippet_m:
                        s = re.sub(r'<[^>]+>', '', snippet_m.group(1)).strip()[:300]
                    print(f'  Title: {html.unescape(t)}')
                    print(f'  URL: {u}')
                    print(f'  Snippet: {html.unescape(s)}')
                    print()
    except Exception as e:
        print(f'Bing error: {e}')
