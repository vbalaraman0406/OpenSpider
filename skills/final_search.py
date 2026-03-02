import urllib.request
import urllib.parse
import re

def search_ddg(query):
    encoded = urllib.parse.quote(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        results = []
        pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        links = re.findall(pattern, html, re.DOTALL)
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        snippets = re.findall(snippet_pattern, html, re.DOTALL)
        for i, (link, title) in enumerate(links[:10]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_snippet = ''
            if i < len(snippets):
                clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            if 'uddg=' in link:
                actual = urllib.parse.unquote(link.split('uddg=')[1].split('&')[0])
            else:
                actual = link
            results.append({'title': clean_title, 'url': actual, 'snippet': clean_snippet})
        return results
    except Exception as e:
        return []

queries = [
    'Portland Tile LLC Vancouver WA phone number reviews rating',
    'All Tile Inc Portland OR bathroom contractor phone reviews',
    'NW Tile Works Portland Oregon phone rating',
    'Precision Tile Portland OR bathroom installer phone reviews',
    'Chase tile installer Portland OR reviews phone',
    'Masterworks Tile Installation Portland phone number rating reviews',
    'RTA Tile LLC Portland Vancouver phone reviews',
    'Pacific Tile Works Portland OR phone reviews rating',
]

for q in queries:
    print(f'\n=== {q} ===')
    results = search_ddg(q)
    for r in results[:4]:
        print(f"  {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  {r['snippet'][:300]}")
        print()
