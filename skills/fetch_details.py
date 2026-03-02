import urllib.request
import re
import json

def fetch_page(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Let me search for specific contractor details with a more targeted query
def search_ddg(query):
    import urllib.parse
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

# Search for specific contractors with phone numbers and ratings
queries = [
    'Hawthorne Tile Portland OR phone number rating reviews',
    'All Tile bathroom contractor Portland phone reviews',
    'Masterworks Tile Installation Vancouver WA phone rating',
    'RTA Tile LLC Vancouver WA phone rating reviews',
    'bathroom tile contractor Portland OR phone number 5 star reviews 2024',
    'NW Tile Works Portland Oregon contractor reviews phone',
    'Pacific Tile Portland bathroom installer reviews rating',
    'bathroom tile installation contractor reviews phone number rating Portland Oregon'
]

contractors = []
for q in queries:
    print(f'\n=== {q} ===')
    results = search_ddg(q)
    for r in results[:5]:
        print(f"  {r['title']}")
        print(f"  {r['url']}")
        print(f"  {r['snippet'][:250]}")
        print()

print('\n=== DONE ===')
