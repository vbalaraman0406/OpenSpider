import urllib.request
import urllib.parse
import json
import re

def ddg_search(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Extract snippets
    snippets = re.findall(r'class="result__snippet">(.*?)</a>', html, re.DOTALL)
    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    links = re.findall(r'class="result__url"[^>]*href="(.*?)"', html, re.DOTALL)
    results = []
    for i in range(min(len(snippets), 8)):
        t = re.sub(r'<[^>]+>', '', titles[i] if i < len(titles) else '')
        s = re.sub(r'<[^>]+>', '', snippets[i])
        l = links[i] if i < len(links) else ''
        results.append(f'Title: {t}\nSnippet: {s}\nURL: {l}')
    return '\n---\n'.join(results)

# Search for Google rating
print('=== Google Rating Search ===')
try:
    r = ddg_search('Fazzolari Custom Homes Renovations Vancouver WA Google reviews rating stars')
    print(r[:1500])
except Exception as e:
    print(f'Error: {e}')

print()
print('=== Yelp Rating Search ===')
try:
    r = ddg_search('Fazzolari Construction Vancouver WA Yelp rating reviews')
    print(r[:1500])
except Exception as e:
    print(f'Error: {e}')

print()
print('=== BBB Rating Search ===')
try:
    r = ddg_search('Fazzolari Custom Homes Renovations BBB rating Vancouver WA')
    print(r[:1000])
except Exception as e:
    print(f'Error: {e}')
