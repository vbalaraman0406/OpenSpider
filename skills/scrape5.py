import urllib.request
import re
import json

# Try Bing search
queries = [
    'best+bathroom+remodel+contractor+Vancouver+WA+reviews',
    'bathroom+tile+vanity+contractor+Vancouver+Washington+98662'
]

results = []
for q in queries:
    url = f'https://www.bing.com/search?q={q}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract search result snippets
        # Bing uses <li class="b_algo"> for results
        blocks = re.findall(r'<li class="b_algo">(.*?)</li>', html, re.DOTALL)
        print(f'\n=== Query: {q} === Found {len(blocks)} results')
        for i, block in enumerate(blocks[:10]):
            # Extract title and URL
            title_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL)
            snippet_match = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
            if title_match:
                link = title_match.group(1)
                title = re.sub(r'<[^>]+>', '', title_match.group(2)).strip()
                snippet = ''
                if snippet_match:
                    snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                print(f'{i+1}. {title}')
                print(f'   URL: {link}')
                print(f'   Snippet: {snippet[:200]}')
                print()
    except Exception as e:
        print(f'Error for {q}: {e}')

# Also try to get BBB page directly
try:
    url = 'https://www.bbb.org/search?find_country=US&find_loc=Vancouver%2C%20WA&find_text=bathroom%20remodel&find_type=Category&page=1'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    resp = urllib.request.urlopen(req, timeout=10)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for business names
    names = re.findall(r'class="[^"]*result-name[^"]*"[^>]*>(.*?)<', html, re.DOTALL)
    ratings = re.findall(r'class="[^"]*rating[^"]*"[^>]*>(.*?)<', html, re.DOTALL)
    print(f'\n=== BBB Results: {len(names)} businesses ===')
    for n in names[:10]:
        clean = re.sub(r'<[^>]+>', '', n).strip()
        if clean:
            print(f'  - {clean}')
except Exception as e:
    print(f'BBB Error: {e}')
