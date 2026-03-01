import urllib.request
import urllib.parse
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

queries = [
    'Iran nuclear program 2025 latest news',
    'Iran Middle East latest news 2025',
    'Iran sanctions 2025',
    'Iran Israel tensions 2025',
    'Iran Houthis Yemen 2025'
]

for q in queries:
    print(f'\n=== Searching: {q} ===')
    url = f'https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8')
        # Parse RSS XML manually
        import re
        items = re.findall(r'<item>(.*?)</item>', data, re.DOTALL)
        for item in items[:5]:
            title = re.search(r'<title>(.*?)</title>', item)
            link = re.search(r'<link/>(.*?)<', item)
            if not link:
                link = re.search(r'<link>(.*?)</link>', item)
            pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
            source = re.search(r'<source[^>]*>(.*?)</source>', item)
            t = title.group(1) if title else 'N/A'
            l = link.group(1).strip() if link else 'N/A'
            d = pubdate.group(1) if pubdate else 'N/A'
            s = source.group(1) if source else 'N/A'
            print(f'Title: {t}')
            print(f'Source: {s}')
            print(f'Date: {d}')
            print(f'Link: {l}')
            print('---')
    except Exception as e:
        print(f'Error: {e}')
