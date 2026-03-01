import urllib.request
import urllib.parse
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def search_ddg(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract result snippets and URLs
        results = []
        # Find result links
        links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:td|div|span)', html, re.DOTALL)
        for i, (link, title) in enumerate(links[:5]):
            title_clean = re.sub(r'<[^>]+>', '', title).strip()
            snip = ''
            if i < len(snippets):
                snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            results.append({'url': link, 'title': title_clean, 'snippet': snip})
        return results
    except Exception as e:
        return [{'error': str(e)}]

queries = [
    'Mountainwood contractor Vancouver WA',
    'Mountainwood bathroom remodel Vancouver WA 98662',
    'Mountainwood construction Vancouver Washington',
    'Mountainwood remodeling Portland metro',
    'Mountainwood LLC contractor Washington state',
    'site:yelp.com Mountainwood Vancouver WA',
    'site:bbb.org Mountainwood Vancouver WA',
]

print('=== SEARCHING FOR MOUNTAINWOOD CONTRACTOR ===')
all_urls = set()
for q in queries:
    print(f'\nQuery: {q}')
    results = search_ddg(q)
    if not results:
        print('  No results')
    for r in results:
        if 'error' in r:
            print(f'  Error: {r["error"]}')
        else:
            print(f'  Title: {r["title"]}')
            print(f'  URL: {r["url"]}')
            print(f'  Snippet: {r["snippet"][:200]}')
            all_urls.add(r['url'])
    print()

# Also try WA state contractor license lookup
print('\n=== WA STATE LICENSE LOOKUP ===')
try:
    wa_url = 'https://secure.lni.wa.gov/verify/Results.aspx?k=m&t=C&s=mountainwood'
    req = urllib.request.Request(wa_url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode('utf-8', errors='ignore')
    # Look for contractor names
    names = re.findall(r'<td[^>]*>(.*?)</td>', html)
    clean_names = [re.sub(r'<[^>]+>', '', n).strip() for n in names if 'mountain' in n.lower()]
    if clean_names:
        print('Found entries:', clean_names[:10])
    else:
        print('No Mountainwood entries found in WA LNI database')
        # Print first 500 chars for debugging
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text).strip()
        print('Page text (first 500):', text[:500])
except Exception as e:
    print(f'WA LNI error: {e}')

print('\n=== SUMMARY ===')
print(f'Total unique URLs found: {len(all_urls)}')
for u in all_urls:
    print(f'  {u}')
