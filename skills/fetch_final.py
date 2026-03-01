import urllib.request
import urllib.parse
import re
import ssl
import time
import json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def ddg_search(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html',
    })
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    html = resp.read().decode('utf-8', errors='ignore')
    results = []
    snippets = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    if not snippets:
        snippets = re.findall(r'class="result__a"[^>]*>(.*?)</a>.*?class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    links = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
    snips = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
    for i, (link, title) in enumerate(links[:8]):
        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        clean_snip = re.sub(r'<[^>]+>', '', snips[i]).strip() if i < len(snips) else ''
        results.append((clean_title, link, clean_snip))
    return results

# Search 1: Yelp bathroom tile Vancouver WA
print("=== SEARCH 1: Yelp bathroom tile contractors Vancouver WA ===")
for title, link, snip in ddg_search('site:yelp.com bathroom tile contractor Vancouver WA'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()

time.sleep(3)

# Search 2: Thumbtack tile Vancouver WA
print("=== SEARCH 2: Thumbtack tile installers Vancouver WA ===")
for title, link, snip in ddg_search('site:thumbtack.com tile installer Vancouver WA reviews'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()

time.sleep(3)

# Search 3: Houzz tile contractors Vancouver WA
print("=== SEARCH 3: Houzz tile contractors Vancouver WA ===")
for title, link, snip in ddg_search('site:houzz.com tile contractors Vancouver WA reviews'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()

time.sleep(3)

# Search 4: Angi bathroom remodel Vancouver WA
print("=== SEARCH 4: Angi bathroom remodel Vancouver WA ===")
for title, link, snip in ddg_search('site:angi.com bathroom remodel tile Vancouver WA'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()

time.sleep(3)

# Search 5: Specific contractors with reviews
print("=== SEARCH 5: Top rated bathroom tile contractors Orchards Vancouver WA ===")
for title, link, snip in ddg_search('bathroom tile contractor Orchards Vancouver WA reviews rated'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()

time.sleep(3)

# Search 6: More specific contractors
print("=== SEARCH 6: Vanity installation tile replacement Vancouver WA contractor ===")
for title, link, snip in ddg_search('vanity installation tile replacement contractor Vancouver WA 98662 reviews'):
    print(f"  {title}")
    print(f"    {snip[:200]}")
    print()
