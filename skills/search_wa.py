import urllib.request
import re
import html as htmlmod

def search_ddg(query):
    url = f'https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    text = resp.read().decode('utf-8', errors='replace')
    # Extract links and snippets
    links = re.findall(r'<a[^>]*rel="nofollow"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', text, re.DOTALL)
    snippets = re.findall(r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>', text, re.DOTALL)
    results = []
    for i in range(min(len(links), 10)):
        title = htmlmod.unescape(re.sub(r'<[^>]+>', '', links[i][1]).strip())
        href = links[i][0]
        snip = htmlmod.unescape(re.sub(r'<[^>]+>', '', snippets[i]).strip()) if i < len(snippets) else ''
        results.append({'title': title, 'url': href, 'snippet': snip[:200]})
    return results

import urllib.parse

print('='*60)
print('SEARCH 1: WA State Contractor License Requirements')
print('='*60)
results1 = search_ddg('Washington state contractor license registration L&I requirements bathroom renovation')
for r in results1:
    print(f"\nTitle: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet']}")

print('\n' + '='*60)
print('SEARCH 2: WA L&I Contractor Verification Lookup Tool')
print('='*60)
results2 = search_ddg('Washington L&I verify contractor license lookup tool site:lni.wa.gov')
for r in results2:
    print(f"\nTitle: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet']}")

print('\n' + '='*60)
print('SEARCH 3: Vancouver WA Permit Requirements Bathroom Remodel')
print('='*60)
results3 = search_ddg('Vancouver WA 98662 building permit requirements bathroom remodel tile plumbing vanity Clark County')
for r in results3:
    print(f"\nTitle: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"Snippet: {r['snippet']}")
