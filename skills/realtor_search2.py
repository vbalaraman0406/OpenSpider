import requests
import json
import re

cities = [
    'Vancouver_WA',
    'Ridgefield_WA',
    'Battle-Ground_WA',
    'Camas_WA',
    'Washougal_WA',
    'Brush-Prairie_WA'
]

all_listings = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'en-US,en;q=0.9'
}

for city in cities:
    url = f'https://www.realtor.com/realestateandhomes-search/{city}/beds-5/baths-2/price-na-600000/age-5'
    try:
        resp = requests.get(url, headers=headers, timeout=20, verify=False)
        html = resp.text
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
            props = data.get('props', {}).get('pageProps', {})
            search_results = props.get('properties', [])
            if not search_results:
                sr = props.get('searchResults', {}).get('home_search', {}).get('properties', [])
                if sr:
                    search_results = sr
            print(f'{city}: Found {len(search_results)} properties')
            for p in search_results:
                loc = p.get('location', {})
                addr = loc.get('address', {})
                address = f"{addr.get('line', '')} {addr.get('city', '')} {addr.get('state_code', '')} {addr.get('postal_code', '')}"
                price = p.get('list_price', 0)
                desc = p.get('description', {})
                beds = desc.get('beds', 0)
                baths_full = desc.get('baths_full', 0)
                baths_half = desc.get('baths_half', 0)
                baths = baths_full + (0.5 * baths_half)
                sqft = desc.get('sqft', 0)
                yr = desc.get('year_built', 0)
                slug = p.get('permalink', '')
                link = f'https://www.realtor.com/realestateandhomes-detail/{slug}' if slug else ''
                if price and price <= 600000 and beds >= 5 and baths >= 2.5 and baths <= 3.0 and yr and yr >= 2017:
                    all_listings.append({
                        'address': address.strip(),
                        'price': price,
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year_built': yr,
                        'link': link,
                        'source': 'Realtor.com'
                    })
        else:
            print(f'{city}: No __NEXT_DATA__ found. HTML length: {len(html)}')
            if 'captcha' in html.lower() or 'robot' in html.lower():
                print(f'{city}: CAPTCHA/bot detection triggered')
    except Exception as e:
        print(f'{city}: Error - {e}')

print(f'\nTotal matching listings: {len(all_listings)}')
for l in all_listings:
    print(json.dumps(l))
