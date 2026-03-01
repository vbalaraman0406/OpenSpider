import urllib.request
import urllib.parse
import re
import json

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"ERROR: {e}"

# Search 1: DuckDuckGo for reliable men LLC Vancouver WA
queries = [
    '"Reliable Men" Vancouver WA remodel site:yelp.com OR site:bbb.org OR site:google.com',
    '"Reliable Men" LLC Vancouver WA contractor',
    'reliablemen.com Vancouver WA',
    '"Reliable Men" Vancouver Washington home remodel reviews',
]

all_urls = []
all_results = []

for q in queries:
    encoded = urllib.parse.quote_plus(q)
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    html = fetch_url(url)
    if html.startswith('ERROR'):
        print(f"Search failed for: {q} -> {html}")
        continue
    
    # Extract URLs and titles
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    
    for i, (link, title) in enumerate(links[:5]):
        if 'uddg=' in link:
            match = re.search(r'uddg=([^&]+)', link)
            if match:
                actual_url = urllib.parse.unquote(match.group(1))
            else:
                actual_url = link
        else:
            actual_url = link
        
        # Skip ad URLs
        if 'bing.com/aclick' in actual_url or 'duckduckgo.com/y.js' in actual_url:
            continue
            
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:300] if i < len(snippets) else 'N/A'
        
        if actual_url not in all_urls:
            all_urls.append(actual_url)
            all_results.append({
                'title': clean_title,
                'url': actual_url,
                'snippet': snippet,
                'query': q
            })

print(f"Found {len(all_results)} unique results:\n")
for r in all_results:
    print(f"Title: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet']}")
    print(f"Query: {r['query']}")
    print("---")
