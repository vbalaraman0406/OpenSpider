import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})

# Try broader searches on sites that worked before
sources = [
    ('Motorsport.com search', 'https://www.motorsport.com/f1/news/?q=chinese+gp+2026+results'),
    ('Crash.net F1', 'https://www.crash.net/f1/results'),
    ('GPFans results', 'https://www.gpfans.com/en/f1-results/'),
    ('F1 official 2026 races', 'https://www.formula1.com/en/results/2026/races'),
    ('Autosport latest', 'https://www.autosport.com/f1/'),
    ('PlanetF1 latest', 'https://www.planetf1.com/f1-news/'),
]

for name, url in sources:
    try:
        resp = session.get(url, timeout=12, allow_redirects=True)
        if resp.status_code == 200:
            html = resp.text
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            lower = text.lower()
            
            # Search for Chinese GP related content
            for kw in ['chinese gp', 'china sprint', 'shanghai', 'sprint qualifying results', 'fp1 results']:
                idx = lower.find(kw)
                if idx > 0:
                    print(f'=== {name} - Found "{kw}" ===')
                    print(text[max(0,idx-100):idx+500])
                    print()
                    break
            
            # Also look for any lap times
            times = re.findall(r'1:\d{2}\.\d{3}', text)
            if times:
                print(f'  Lap times on {name}: {times[:10]}')
        else:
            print(f'{name}: HTTP {resp.status_code}')
    except Exception as e:
        print(f'Error {name}: {e}')
    print()
