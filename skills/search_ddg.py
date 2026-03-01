import urllib.request
import urllib.parse
import re
import html
import time

def search_ddg(query):
    encoded = urllib.parse.quote_plus(query)
    url = f'https://html.duckduckgo.com/html/?q={encoded}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode('utf-8', errors='replace')
        # Extract result snippets
        results = []
        # DuckDuckGo HTML results have class="result__a" for links and class="result__snippet" for snippets
        link_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>'
        snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
        links = re.findall(link_pattern, data, re.DOTALL)
        snippets = re.findall(snippet_pattern, data, re.DOTALL)
        for i, (href, title) in enumerate(links[:10]):
            clean_title = re.sub(r'<[^>]+>', '', title).strip()
            clean_title = html.unescape(clean_title)
            # Clean href - DDG wraps URLs
            if 'uddg=' in href:
                m = re.search(r'uddg=([^&]+)', href)
                if m:
                    href = urllib.parse.unquote(m.group(1))
            snip = ''
            if i < len(snippets):
                snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                snip = html.unescape(snip)
            results.append({'title': clean_title, 'url': href, 'snippet': snip})
        return results
    except Exception as e:
        return [{'title': f'ERROR: {e}', 'url': '', 'snippet': ''}]

queries = [
    'bathroom remodel contractor Vancouver WA 98662 reviews ratings',
    'best bathroom tile contractor Vancouver WA phone number',
    'bathroom vanity replacement contractor Vancouver Washington rated',
    'BBB bathroom remodel contractor Vancouver WA',
    'houzz bathroom remodel Vancouver WA contractors',
]

all_results = []
for q in queries:
    print(f'\n=== Query: {q} ===')
    results = search_ddg(q)
    for r in results:
        print(f"  TITLE: {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  SNIPPET: {r['snippet'][:200]}")
        print()
        all_results.append(r)
    time.sleep(2)

# Now extract contractor info from snippets
print('\n\n=== EXTRACTED CONTRACTOR DATA ===')
phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
rating_pattern = r'(\d+\.?\d*)\s*(?:star|/5|out of|rating|★)'
for r in all_results:
    phones = re.findall(phone_pattern, r['snippet'] + ' ' + r['title'])
    ratings = re.findall(rating_pattern, r['snippet'].lower() + ' ' + r['title'].lower())
    if phones or ratings or any(kw in r['snippet'].lower() for kw in ['bathroom', 'remodel', 'tile', 'vanity', 'contractor']):
        print(f"Company/Title: {r['title']}")
        print(f"URL: {r['url']}")
        if phones:
            print(f"Phone(s): {', '.join(phones)}")
        if ratings:
            print(f"Rating(s): {', '.join(ratings)}")
        print(f"Snippet: {r['snippet'][:250]}")
        print('---')
