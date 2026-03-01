import urllib.request
import urllib.parse
import re
import json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

contractors = [
    'Reliable Men contractor Vancouver WA',
    'Lets Remodel contractor Vancouver WA',
    'Fazzolari contractor Vancouver WA',
    'Mountainwood contractor Vancouver WA',
    'Beto and Son contractor Vancouver WA'
]

for q in contractors:
    print(f'\n=== {q} ===')
    # Try Google search
    try:
        url = 'https://www.google.com/search?' + urllib.parse.urlencode({'q': q})
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract snippets
        snippets = re.findall(r'<span[^>]*>([^<]{40,300})</span>', html)
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
        links = re.findall(r'href="/url\?q=(https?://[^&"]+)', html)
        print(f'Titles: {titles[:5]}')
        print(f'Links: {links[:5]}')
        for s in snippets[:3]:
            clean = re.sub(r'<[^>]+>', '', s).strip()
            if len(clean) > 30:
                print(f'Snippet: {clean}')
    except Exception as e:
        print(f'Google error: {e}')
    
    # Try DuckDuckGo lite
    try:
        url2 = 'https://lite.duckduckgo.com/lite/?' + urllib.parse.urlencode({'q': q})
        req2 = urllib.request.Request(url2, headers=headers)
        resp2 = urllib.request.urlopen(req2, timeout=10)
        html2 = resp2.read().decode('utf-8', errors='ignore')
        results = re.findall(r'<a[^>]+href="(https?://[^"]+)"[^>]*class="result-link"[^>]*>(.*?)</a>', html2)
        snippets2 = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', html2, re.DOTALL)
        if results:
            for r in results[:3]:
                print(f'DDG Link: {r[0]} | Title: {re.sub("<[^>]+>", "", r[1])}')
        if snippets2:
            for s in snippets2[:3]:
                print(f'DDG Snippet: {re.sub("<[^>]+>", "", s).strip()}')
        if not results and not snippets2:
            # Try extracting any links
            all_links = re.findall(r'href="(https?://[^"]+)"', html2)
            print(f'DDG all links: {all_links[:5]}')
    except Exception as e:
        print(f'DDG error: {e}')
