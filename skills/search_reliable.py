import urllib.request
import re

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Bing search 1
print('=== BING 1: Reliable Men contractor Vancouver WA ===')
html = fetch('https://www.bing.com/search?q=Reliable+Men+contractor+Vancouver+WA+bathroom+remodel+reviews')
links = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html)
for u, t in links[:20]:
    ct = re.sub(r'<[^>]+>', '', t).strip()
    if ct and len(ct) > 8 and 'bing' not in u.lower() and 'microsoft' not in u.lower() and 'go.microsoft' not in u.lower():
        print(f'{ct[:120]} | {u[:200]}')
snippets = re.findall(r'<p[^>]*>(.*?)</p>', html)
for s in snippets[:15]:
    c = re.sub(r'<[^>]+>', '', s).strip()
    if c and len(c) > 25:
        print(f'SNIP: {c[:250]}')

print()
print('=== BING 2: exact match ===')
html2 = fetch('https://www.bing.com/search?q=%22Reliable+Men%22+Vancouver+WA+contractor+rating+phone')
links2 = re.findall(r'<a[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', html2)
for u, t in links2[:20]:
    ct = re.sub(r'<[^>]+>', '', t).strip()
    if ct and len(ct) > 8 and 'bing' not in u.lower() and 'microsoft' not in u.lower():
        print(f'{ct[:120]} | {u[:200]}')
snippets2 = re.findall(r'<p[^>]*>(.*?)</p>', html2)
for s in snippets2[:15]:
    c = re.sub(r'<[^>]+>', '', s).strip()
    if c and len(c) > 25:
        print(f'SNIP: {c[:250]}')
