import urllib.request
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# Let me try to get content from some key news sources directly
urls = [
    ('PBS - Fact-checking Trump on Iran strikes', 'https://www.pbs.org/newshour/politics'),
    ('Al Jazeera Iran', 'https://www.aljazeera.com/tag/iran/'),
    ('Reuters Iran', 'https://www.reuters.com/world/middle-east/'),
]

for name, url in urls:
    print(f'\n=== {name} ===')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract headlines and snippets
        # Look for Iran-related content
        iran_sections = []
        lines = html.split('\n')
        for line in lines:
            if 'iran' in line.lower() or 'houthi' in line.lower() or 'nuclear' in line.lower():
                # Clean HTML tags
                clean = re.sub(r'<[^>]+>', ' ', line).strip()
                clean = re.sub(r'\s+', ' ', clean)
                if len(clean) > 20 and len(clean) < 500:
                    iran_sections.append(clean)
        for s in iran_sections[:10]:
            print(f'  - {s}')
    except Exception as e:
        print(f'Error: {e}')

# Also search for more specific recent news
print('\n=== Additional Google News: Iran nuclear talks March 2026 ===')
import urllib.parse
for q in ['Iran nuclear talks March 2026', 'Iran sanctions 2026', 'Iran military strikes 2025 2026', 'Iran diplomacy Trump 2026']:
    url = f'https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=en-US&gl=US&ceid=US:en'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8')
        items = re.findall(r'<item>(.*?)</item>', data, re.DOTALL)
        print(f'\n--- {q} ---')
        for item in items[:4]:
            title = re.search(r'<title>(.*?)</title>', item)
            pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
            source = re.search(r'<source[^>]*>(.*?)</source>', item)
            t = title.group(1) if title else 'N/A'
            d = pubdate.group(1) if pubdate else 'N/A'
            s = source.group(1) if source else 'N/A'
            print(f'  [{d}] {t} ({s})')
    except Exception as e:
        print(f'Error: {e}')
