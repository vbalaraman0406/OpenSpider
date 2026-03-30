import requests
import json
import re
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Upgrade-Insecure-Requests': '1',
})
session.get('https://www.redfin.com/', timeout=15, verify=False)

url = 'https://www.redfin.com/zipcode/98682/filter/property-type=house,max-price=600k,min-beds=5,min-year-built=2017'
resp = session.get(url, timeout=15, verify=False)
html = resp.text

# Save full HTML
with open('redfin_page.html', 'w') as f:
    f.write(html)

print(f'Page length: {len(html)}')

# Look for all script tags with data
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'Found {len(scripts)} script tags')

for i, s in enumerate(scripts):
    if len(s) > 100:
        # Check for data patterns
        if 'streetLine' in s or 'homes' in s or 'listing' in s.lower() or 'property' in s.lower():
            print(f'\nScript {i} (len={len(s)}): Contains listing data!')
            print(s[:500])
        elif '__reactServerState' in s or 'InitialContext' in s or 'ServerState' in s:
            print(f'\nScript {i} (len={len(s)}): Contains React state!')
            print(s[:500])

# Also search for specific data patterns anywhere in HTML
patterns = ['streetLine', 'homeCard', 'listingId', 'mlsId', 'searchResults', 'propertyId']
for p in patterns:
    count = html.count(p)
    if count > 0:
        idx = html.index(p)
        print(f'\nPattern "{p}" found {count} times. Context at first occurrence:')
        print(html[max(0,idx-50):idx+200])
