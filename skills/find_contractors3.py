import urllib.request
import urllib.parse
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f'ERROR: {e}'

# Try Houzz for Vancouver WA bathroom remodelers
print('=== HOUZZ SEARCH ===')
url = 'https://www.houzz.com/professionals/bathroom-remodeling-and-addition/vancouver-wa-us-probr0-bo~t_11788~r_4857973'
html = fetch(url)
if not html.startswith('ERROR'):
    # Extract professional names
    names = re.findall(r'"name"\s*:\s*"([^"]+)"', html)
    # Filter unique, relevant names
    seen = set()
    for n in names:
        if n not in seen and len(n) > 3 and len(n) < 80:
            seen.add(n)
            print(f'  - {n}')
            if len(seen) >= 15:
                break
else:
    print(html)

# Try a broader DuckDuckGo search with better query
print('\n=== DUCKDUCKGO - Better Query ===')
queries = [
    'site:yelp.com bathroom remodel Vancouver WA',
    'best bathroom tile contractor Vancouver WA 2024 reviews rating',
]

for q in queries:
    url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}'
    html = fetch(url)
    if html.startswith('ERROR'):
        print(f'  Query failed: {html}')
        continue
    results = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', html, re.DOTALL)
    print(f'\nQuery: {q}')
    for i, (link, title) in enumerate(results[:10]):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()[:200] if i < len(snippets) else ''
        actual_url = re.search(r'uddg=([^&]+)', link)
        if actual_url:
            link = urllib.parse.unquote(actual_url.group(1))
        # Skip ad URLs
        if 'duckduckgo.com/y.js' in link:
            continue
        print(f'  {i+1}. {title_clean}')
        print(f'     {link}')
        print(f'     {snip}')
        print()

# Also try Google Maps embed / places type search
print('\n=== THUMBTACK SEARCH ===')
url = 'https://www.thumbtack.com/wa/vancouver/tile-installers/'
html = fetch(url)
if not html.startswith('ERROR'):
    names = re.findall(r'"displayName"\s*:\s*"([^"]+)"', html)
    ratings = re.findall(r'"averageRating"\s*:\s*([\d.]+)', html)
    review_counts = re.findall(r'"numReviews"\s*:\s*(\d+)', html)
    if not names:
        names = re.findall(r'"name"\s*:\s*"([^"]+?)"', html)
    seen = set()
    for i, n in enumerate(names):
        if n not in seen and len(n) > 3 and 'Thumbtack' not in n and 'tile' not in n.lower() and 'install' not in n.lower():
            continue
        if n not in seen and len(n) > 3:
            seen.add(n)
            r = ratings[i] if i < len(ratings) else 'N/A'
            rc = review_counts[i] if i < len(review_counts) else 'N/A'
            print(f'  - {n} | Rating: {r} | Reviews: {rc}')
            if len(seen) >= 10:
                break
else:
    print(html)
