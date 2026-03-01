import urllib.request
import urllib.parse
import re

query = 'Fazzolari contractor Vancouver WA bathroom remodel reviews'
url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
try:
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract result snippets
    # DuckDuckGo results are in <a class="result__a" ...> and <a class="result__snippet" ...>
    links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    
    print(f'Found {len(links)} results')
    for i, (link, title) in enumerate(links[:15]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_snippet = ''
        if i < len(snippets):
            clean_snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:200]
        print(f'\n--- Result {i+1} ---')
        print(f'Title: {clean_title}')
        print(f'URL: {link}')
        print(f'Snippet: {clean_snippet}')
except Exception as e:
    print(f'Error: {e}')

# Also try searching for just 'Fazzolari Custom Homes' or 'Fazzolari Construction'
print('\n\n=== SECOND SEARCH ===')
query2 = 'Fazzolari Custom Homes Vancouver WA'
url2 = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query2)
req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    html2 = resp2.read().decode('utf-8', errors='ignore')
    links2 = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>([^<]+)', html2)
    snippets2 = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html2, re.DOTALL)
    print(f'Found {len(links2)} results')
    for i, (link, title) in enumerate(links2[:10]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_snippet = ''
        if i < len(snippets2):
            clean_snippet = re.sub(r'<[^>]+>', '', snippets2[i]).strip()[:200]
        print(f'\n--- Result {i+1} ---')
        print(f'Title: {clean_title}')
        print(f'URL: {link}')
        print(f'Snippet: {clean_snippet}')
except Exception as e:
    print(f'Error: {e}')
