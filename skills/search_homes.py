import requests
import json
import re
from urllib.parse import quote

results = []

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Try Zillow API endpoint
areas = ['Vancouver WA', 'Ridgefield WA', 'Battle Ground WA', 'Camas WA', 'Washougal WA', 'Brush Prairie WA']

print('=== Attempting Redfin API ===')
for area in areas:
    try:
        # Redfin has a more accessible API
        search_url = f'https://www.redfin.com/stingray/do/location-autocomplete?location={quote(area)}&v=2'
        r = requests.get(search_url, headers=headers, timeout=10)
        print(f'Redfin autocomplete for {area}: status={r.status_code}, len={len(r.text)}')
        if r.status_code == 200:
            text = r.text
            if text.startswith('{}&&'):
                text = text[4:]
            data = json.loads(text)
            print(f'  Parsed: {json.dumps(data, indent=2)[:500]}')
    except Exception as e:
        print(f'  Error: {e}')

print('\n=== Attempting Realtor.com API ===')
for area in areas:
    try:
        city = area.replace(' WA', '').replace(' ', '-')
        url = f'https://www.realtor.com/api/v1/hulk_main_srp?client_id=rdc-x&schema=vesta&query=%7B%22status%22%3A%22for_sale%22%2C%22primary%22%3Atrue%2C%22search_location%22%3A%7B%22location%22%3A%22{quote(area)}%22%7D%2C%22beds_min%22%3A5%2C%22baths_min%22%3A2%2C%22price_max%22%3A600000%2C%22year_built_min%22%3A2017%7D'
        r = requests.get(url, headers=headers, timeout=10)
        print(f'Realtor.com for {area}: status={r.status_code}, len={len(r.text)[:200]}')
    except Exception as e:
        print(f'  Error: {e}')

print('\n=== Trying Google Search for listings ===')
search_queries = [
    'site:zillow.com Vancouver WA 5 bedroom house for sale under 600000 built 2017',
    'site:redfin.com Vancouver WA 5 bedroom 2.5 bath house under 600000',
    'Vancouver WA 5 bedroom house for sale under 600000 built after 2017',
    'Ridgefield WA 5 bedroom house for sale under 600000',
    'Battle Ground WA 5 bedroom house for sale under 600000',
    'Camas WA 5 bedroom house for sale under 600000',
]

for q in search_queries:
    try:
        url = f'https://www.google.com/search?q={quote(q)}&num=10'
        r = requests.get(url, headers=headers, timeout=10)
        print(f'\nGoogle: "{q[:60]}..." status={r.status_code}')
        # Extract snippets
        snippets = re.findall(r'<span[^>]*>([^<]*\$[^<]*)</span>', r.text)
        for s in snippets[:5]:
            print(f'  ${s}')
        # Extract links
        links = re.findall(r'href="(https?://(?:www\.)?(?:zillow|redfin|realtor)\.com/[^"]+)"', r.text)
        for l in links[:5]:
            print(f'  Link: {l}')
    except Exception as e:
        print(f'  Error: {e}')

print('\nDone with initial search.')
