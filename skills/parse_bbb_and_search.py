import urllib.request
import urllib.parse
import re
import ssl
import time
import json

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Parse BBB page
print('=== BBB Parse ===')
url = 'https://www.bbb.org/search?find_country=US&find_text=bathroom+remodel&find_loc=Vancouver%2C+WA&find_type=Category&page=1'
html = fetch(url)
if not html.startswith('ERROR'):
    # Find next-data JSON
    nd = re.findall(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if nd:
        try:
            data = json.loads(nd[0])
            results = data.get('props',{}).get('pageProps',{}).get('searchResults',{}).get('results',[])
            if not results:
                # Try alternate path
                sp = data.get('props',{}).get('pageProps',{})
                print(f'  PageProps keys: {list(sp.keys())[:10]}')
            for r in results[:10]:
                print(f"  {r.get('businessName','?')} | {r.get('rating','?')} | {r.get('phone','?')}")
        except:
            print('  JSON parse failed')
    else:
        # Try other patterns
        biz_names = re.findall(r'class="[^"]*result-name[^"]*"[^>]*>([^<]+)', html)
        biz_links = re.findall(r'href="(/profile/[^"]+)"', html)
        if biz_names:
            for n in biz_names[:10]:
                print(f'  {n.strip()}')
        elif biz_links:
            for l in biz_links[:10]:
                print(f'  https://www.bbb.org{l}')
        else:
            # Just find any business-like patterns
            names = re.findall(r'"name"\s*:\s*"([^"]{5,80})"', html)
            unique = []
            seen = set()
            for n in names:
                if n not in seen and 'BBB' not in n and 'script' not in n.lower():
                    seen.add(n)
                    unique.append(n)
            print(f'  Names found: {unique[:15]}')

# Try DuckDuckGo JSON API
time.sleep(3)
print('\n=== DuckDuckGo Instant Answer API ===')
url = 'https://api.duckduckgo.com/?q=bathroom+remodel+contractor+Vancouver+WA&format=json'
html = fetch(url)
if not html.startswith('ERROR'):
    try:
        data = json.loads(html)
        if data.get('RelatedTopics'):
            for t in data['RelatedTopics'][:5]:
                if isinstance(t, dict) and 'Text' in t:
                    print(f"  {t['Text'][:200]}")
        if data.get('Results'):
            for r in data['Results'][:5]:
                print(f"  {r.get('Text','')[:200]}")
        if not data.get('RelatedTopics') and not data.get('Results'):
            print(f'  Keys: {list(data.keys())}')
            print(f'  Abstract: {data.get("Abstract","none")[:200]}')
    except:
        print(f'  Raw: {html[:500]}')

# Try searching DuckDuckGo one more time with fresh approach
time.sleep(3)
print('\n=== DuckDuckGo Search - Specific ===')
for q in ['bathroom remodel Vancouver WA 98662 yelp reviews contractor', 'vanity tile replacement Vancouver Washington contractor reviews 2024']:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'  Failed: {html}')
        continue
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    print(f'\n  Query: {q}')
    shown = 0
    for i, (link, title) in enumerate(results[:10]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:250] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url:
            link = urllib.parse.unquote(actual_url.group(1))
        if 'duckduckgo.com/y.js' in link:
            continue
        print(f'  {title_clean}')
        print(f'  {link}')
        print(f'  {snip}')
        print()
        shown += 1
        if shown >= 5:
            break
    time.sleep(2)
