import urllib.request
import urllib.parse
import re
import json

def search_ddg(query):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        return f'ERROR: {e}'

def extract_results(html):
    # Extract result titles and snippets
    results = []
    # DuckDuckGo HTML results have class="result__a" for titles and "result__snippet" for snippets
    title_pattern = re.compile(r'class="result__a"[^>]*>(.*?)</a>', re.DOTALL)
    snippet_pattern = re.compile(r'class="result__snippet"[^>]*>(.*?)</td>', re.DOTALL)
    url_pattern = re.compile(r'class="result__url"[^>]*>(.*?)</a>', re.DOTALL)
    
    titles = title_pattern.findall(html)
    snippets = snippet_pattern.findall(html)
    urls = url_pattern.findall(html)
    
    for i in range(len(titles)):
        t = re.sub(r'<[^>]+>', '', titles[i]).strip()
        s = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ''
        u = re.sub(r'<[^>]+>', '', urls[i]).strip() if i < len(urls) else ''
        results.append({'title': t, 'snippet': s, 'url': u})
    return results

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662',
    'top bathroom tile contractors Vancouver Washington reviews',
    'bathroom vanity replacement contractor Vancouver WA ratings',
    'bathroom renovation contractor Vancouver WA 98662 5 star'
]

all_results = []
for q in queries:
    print(f'\n=== Query: {q} ===')
    html = search_ddg(q)
    if html.startswith('ERROR'):
        print(html)
        continue
    results = extract_results(html)
    print(f'Found {len(results)} results')
    for r in results[:10]:
        print(f"Title: {r['title']}")
        print(f"URL: {r['url']}")
        print(f"Snippet: {r['snippet'][:200]}")
        print('---')
        all_results.append(r)

# Now extract contractor names, ratings, phones from snippets
print('\n\n=== EXTRACTED CONTRACTORS ===')
contractors = {}
phone_re = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
rating_re = re.compile(r'(\d\.\d)\s*(?:star|/5|out of|rating|★)', re.IGNORECASE)
review_re = re.compile(r'(\d+)\s*(?:review|rating)', re.IGNORECASE)

for r in all_results:
    text = r['title'] + ' ' + r['snippet']
    phones = phone_re.findall(text)
    ratings = rating_re.findall(text)
    reviews = review_re.findall(text)
    # Skip generic listing sites
    skip = ['yelp.com', 'angi.com', 'homeadvisor.com', 'thumbtack.com', 'houzz.com', 'bbb.org']
    is_listing = any(s in r['url'].lower() for s in skip)
    
    name = r['title'].split(' - ')[0].split(' | ')[0].strip()
    if len(name) > 5:
        key = name.lower()[:30]
        if key not in contractors:
            contractors[key] = {
                'name': name,
                'rating': ratings[0] if ratings else '',
                'reviews': reviews[0] if reviews else '',
                'phone': phones[0] if phones else '',
                'url': r['url'],
                'source': 'listing' if is_listing else 'direct',
                'snippet': r['snippet'][:150]
            }

for c in contractors.values():
    print(json.dumps(c))
