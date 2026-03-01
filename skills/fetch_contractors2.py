import urllib.request
import urllib.parse
import re
import ssl
import json
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    resp = urllib.request.urlopen(req, timeout=20, context=ctx)
    return resp.read().decode('utf-8', errors='ignore')

# Try multiple Google searches to find contractors on specific platforms
searches = [
    'site:thumbtack.com bathroom tile contractor Vancouver WA 98662',
    'site:angi.com bathroom remodeling Vancouver WA Orchards',
    'site:bbb.org bathroom remodeling Vancouver WA',
    'bathroom tile floor vanity contractor Orchards Vancouver WA 98662 reviews',
    'site:nextdoor.com bathroom contractor Vancouver WA recommended',
]

for query in searches:
    print(f"\n===== Search: {query} =====")
    encoded = urllib.parse.quote_plus(query)
    url = f'https://www.google.com/search?q={encoded}&num=10'
    try:
        html = fetch(url)
        # Extract titles and URLs from Google results
        # Pattern for result links
        results = re.findall(r'<a[^>]+href="(https?://(?!www\.google)[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
        seen = set()
        count = 0
        for href, title_html in results:
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            if len(title) > 10 and href not in seen and 'google' not in href:
                seen.add(href)
                count += 1
                print(f"  {count}. {title[:100]}")
                print(f"     URL: {href[:120]}")
                if count >= 5:
                    break
        if count == 0:
            # Try alternate pattern
            titles2 = re.findall(r'<h3[^>]*>(.*?)</h3>', html)
            for t in titles2[:5]:
                clean = re.sub(r'<[^>]+>', '', t).strip()
                print(f"  - {clean}")
            if not titles2:
                print(f"  No results parsed. HTML length: {len(html)}")
                # Check if blocked
                if 'captcha' in html.lower() or 'unusual traffic' in html.lower():
                    print("  ** Google CAPTCHA detected **")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(4)
