import urllib.request
import re
import json

def search_ddg(query):
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets
        results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</span>', html, re.DOTALL)
        return results[:5]
    except Exception as e:
        return [('error', str(e), '')]

import urllib.parse

queries = [
    'Reliable Men contractor Vancouver WA bathroom remodel reviews',
    'Reliable Men LLC Vancouver WA',
    'Let\'s Remodel Vancouver WA contractor reviews',
    'Lets Remodel LLC Vancouver WA bathroom',
    'Beto and Son contractor Vancouver WA remodel',
    'Beto and Son construction Vancouver WA',
]

for q in queries:
    print(f'\n=== Query: {q} ===')
    results = search_ddg(q)
    if not results:
        print('No results found')
    for url, title, snippet in results:
        title_clean = re.sub(r'<[^>]+>', '', title)
        snippet_clean = re.sub(r'<[^>]+>', '', snippet)
        print(f'  URL: {url}')
        print(f'  Title: {title_clean}')
        print(f'  Snippet: {snippet_clean[:200]}')
        print()
