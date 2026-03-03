import urllib.request
import ssl
import re

ssl._create_default_https_context = ssl._create_unverified_context

sources = [
    ('Reuters', 'https://www.reuters.com/world/middle-east/'),
    ('BBC', 'https://www.bbc.com/news/topics/cg41ylwvggnt'),
    ('Al Jazeera', 'https://www.aljazeera.com/tag/iran/'),
]

for name, url in sources:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        # Extract headlines containing Iran
        # Look for title/headline patterns
        titles = re.findall(r'<(?:h[1-4]|a|span)[^>]*>([^<]*[Ii]ran[^<]*)</(?:h[1-4]|a|span)>', html)
        # Also try data-testid or aria-label patterns
        titles2 = re.findall(r'(?:title|aria-label|alt)="([^"]*[Ii]ran[^"]*?)"', html)
        all_titles = list(dict.fromkeys(titles + titles2))  # dedupe preserving order
        if all_titles:
            print(f'\n=== {name} ===')
            for t in all_titles[:10]:
                t = t.strip()
                if len(t) > 15 and len(t) < 200:
                    print(f'  - {t}')
        else:
            print(f'\n=== {name} === No Iran headlines found in HTML')
    except Exception as e:
        print(f'\n=== {name} === Error: {str(e)[:100]}')
