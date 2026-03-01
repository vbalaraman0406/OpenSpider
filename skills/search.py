import urllib.request
import re
import html

def search_bing(query):
    url = f'https://www.bing.com/search?q={query.replace(" ", "+")}'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read().decode('utf-8', errors='ignore')
        return data
    except Exception as e:
        return f'ERROR: {e}'

def extract_results(html_text):
    # Extract search result blocks from Bing
    results = []
    # Bing uses <li class="b_algo"> for organic results
    blocks = re.findall(r'<li class="b_algo">(.*?)</li>', html_text, re.DOTALL)
    for block in blocks:
        # Extract title
        title_m = re.search(r'<h2><a[^>]*>(.*?)</a></h2>', block, re.DOTALL)
        title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip() if title_m else ''
        # Extract URL
        url_m = re.search(r'<h2><a[^>]*href="([^"]+)"', block, re.DOTALL)
        url = url_m.group(1) if url_m else ''
        # Extract snippet
        snip_m = re.search(r'<p[^>]*>(.*?)</p>', block, re.DOTALL)
        snippet = re.sub(r'<[^>]+>', '', snip_m.group(1)).strip() if snip_m else ''
        snippet = html.unescape(snippet)
        title = html.unescape(title)
        if title:
            results.append({'title': title, 'url': url, 'snippet': snippet})
    return results

queries = [
    'best rated bathroom remodel contractors Vancouver WA 98662 phone number reviews',
    'top bathroom tile vanity contractors Vancouver Washington ratings phone',
    'bathroom renovation contractors Vancouver WA reviews phone number',
]

all_results = []
for q in queries:
    print(f'\n=== Query: {q} ===')
    raw = search_bing(q)
    results = extract_results(raw)
    if not results:
        print(f'No results parsed. HTML length: {len(raw)}')
        # Try to find any useful text
        text = re.sub(r'<[^>]+>', ' ', raw)
        text = re.sub(r'\s+', ' ', text)
        # Look for phone numbers and business names
        phones = re.findall(r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}', text)
        print(f'Phone numbers found: {phones[:10]}')
        # Look for ratings
        ratings = re.findall(r'(\d\.\d)\s*(?:star|rating|/5)', text, re.I)
        print(f'Ratings found: {ratings[:10]}')
    else:
        for r in results:
            print(f"Title: {r['title']}")
            print(f"URL: {r['url']}")
            print(f"Snippet: {r['snippet'][:200]}")
            print('---')
            all_results.append(r)

print(f'\nTotal results: {len(all_results)}')
