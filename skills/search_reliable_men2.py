import urllib.request
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Try multiple Bing searches with different queries
queries = [
    '"Reliable+Men"+remodel+Vancouver+WA+98662',
    '"Reliable+Men"+LLC+Vancouver+WA',
    '"Reliable+Men"+contractor+Vancouver+Washington',
    'Reliable+Men+Remodeling+Vancouver+WA+phone',
]

for q in queries:
    url = f'https://www.bing.com/search?q={q}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract search result snippets - Bing uses <li class="b_algo">
        results = re.findall(r'<li class="b_algo">(.*?)</li>', html, re.DOTALL)
        print(f'\n=== Query: {q} ===')
        print(f'Found {len(results)} search results')
        
        for i, r in enumerate(results[:5]):
            # Extract title and URL
            title_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r)
            url_found = title_match.group(1) if title_match else 'N/A'
            title_text = re.sub(r'<[^>]+>', '', title_match.group(2)) if title_match else 'N/A'
            
            # Extract snippet
            snippet = re.sub(r'<[^>]+>', ' ', r)
            snippet = re.sub(r'\s+', ' ', snippet).strip()
            
            print(f'\nResult {i+1}:')
            print(f'  Title: {title_text[:100]}')
            print(f'  URL: {url_found[:150]}')
            print(f'  Snippet: {snippet[:300]}')
    except Exception as e:
        print(f'\n=== Query: {q} ===')
        print(f'Error: {str(e)[:200]}')
