import urllib.request
import urllib.parse
import json
import re
import html

def search_web(query):
    """Simple web search using DuckDuckGo HTML"""
    encoded = urllib.parse.quote_plus(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = []
        # Find result blocks
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', data, re.DOTALL)
        titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', data, re.DOTALL)
        urls = re.findall(r'class="result__url"[^>]*>(.*?)</a>', data, re.DOTALL)
        for i in range(min(len(snippets), 8)):
            t = re.sub(r'<[^>]+>', '', titles[i] if i < len(titles) else '').strip()
            s = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            u = re.sub(r'<[^>]+>', '', urls[i] if i < len(urls) else '').strip()
            results.append({'title': html.unescape(t), 'snippet': html.unescape(s), 'url': u})
        return results
    except Exception as e:
        return [{'error': str(e)}]

queries = [
    'bathroom floor tile replacement cost per square foot 2025',
    'bathroom wall tile installation cost per sq ft 2025',
    'bathroom vanity replacement cost with labor 2025',
    'ceramic vs porcelain vs natural stone tile cost comparison 2025'
]

for q in queries:
    print(f'\n=== QUERY: {q} ===')
    results = search_web(q)
    for r in results[:5]:
        if 'error' in r:
            print(f'  ERROR: {r["error"]}')
        else:
            print(f'  [{r["title"]}]')
            print(f'  URL: {r["url"]}')
            print(f'  {r["snippet"]}')
            print()
