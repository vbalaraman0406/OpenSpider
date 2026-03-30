import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-CA,en;q=0.9',
})

urls = [
    ('Canada', 'https://downdetector.ca/status/bmo/'),
]

for label, url in urls:
    try:
        resp = session.get(url, timeout=15, allow_redirects=True)
        html = resp.text
        print(f'=== {label} ===')
        print(f'URL: {url}')
        print(f'Final URL: {resp.url}')
        print(f'Status Code: {resp.status_code}')
        print(f'HTML length: {len(html)}')
        
        title = re.findall(r'<title>([^<]+)</title>', html)
        if title:
            print(f'Title: {title[0]}')
        
        # Status indicators
        for pat in [r'(No problems at [^<"]+)', r'(Problems at [^<"]+)', r'(Possible problems at [^<"]+)', r'(User reports indicate[^<"]+)']:
            matches = re.findall(pat, html, re.IGNORECASE)
            if matches:
                print(f'STATUS: {matches[0].strip()}')
        
        # Report counts
        report_matches = re.findall(r'(\d+)\s*report', html, re.IGNORECASE)
        if report_matches:
            print(f'Report counts found: {report_matches[:10]}')
        
        # Context around key words
        for kw in ['problems', 'outage', 'baseline', 'report']:
            idx = html.lower().find(kw)
            if idx >= 0:
                snippet = html[max(0,idx-80):idx+150]
                snippet = re.sub(r'<[^>]+>', ' ', snippet).strip()
                snippet = re.sub(r'\s+', ' ', snippet)
                print(f'[{kw}]: {snippet[:200]}')
        
        print()
    except Exception as e:
        print(f'=== {label} === ERROR: {e}')
