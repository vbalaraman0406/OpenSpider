import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
})

# First visit Zillow homepage to get cookies
try:
    r = session.get('https://www.zillow.com/', timeout=15)
    print(f'Homepage: {r.status_code}')
except:
    print('Homepage failed')

areas = [
    'vancouver-wa',
    'ridgefield-wa', 
    'battle-ground-wa',
    'camas-wa',
    'washougal-wa',
    'brush-prairie-wa',
]

all_listings = []

for slug in areas:
    # Use simple URL - Zillow will return all houses, we filter client-side
    url = f'https://www.zillow.com/{slug}/houses/'
    print(f'\nFetching: {slug}')
    try:
        resp = session.get(url, timeout=30)
        print(f'  Status: {resp.status_code}, Size: {len(resp.text)}')
        
        if resp.status_code != 200:
            continue
            
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if not match:
            print('  No __NEXT_DATA__ found')
            if 'captcha' in resp.text.lower():
                print('  CAPTCHA detected!')
            continue
            
        data = json.loads(match.group(1))
        props = data.get('props', {}).get('pageProps', {})
        sr = props.get('searchPageState', {}).get('cat1', {}).get('searchResults', {})
        results = sr.get('listResults', [])
        print(f'  Results: {len(results)}')
        
        for item in results:
            hdp = item.get('hdpData', {}).get('homeInfo', {})
            addr = item.get('address', hdp.get('streetAddress', 'N/A'))
            price_raw = hdp.get('price', item.get('unformattedPrice', 0))
            beds = item.get('beds', hdp.get('bedrooms', 0))
            baths = item.get('baths', hdp.get('bathrooms', 0))
            sqft = item.get('area', hdp.get('livingArea', 'N/A'))
            year = hdp.get('yearBuilt', 0)
            detail = item.get('detailUrl', '')
            if detail and not detail.startswith('http'):
                detail = 'https://www.zillow.com' + detail
            
            try:
                bd = int(beds) if beds else 0
                ba = float(baths) if baths else 0
                p = int(price_raw) if price_raw else 999999
                yr = int(year) if year else 0
            except:
                bd, ba, p, yr = 0, 0, 999999, 0
            
            # Filter: 5+ beds, 2.5-3 baths, under $600K, built 2017+
            if bd >= 5 and ba >= 2.5 and ba <= 3.0 and p <= 600000 and yr >= 2017:
                entry = {
                    'address': addr,
                    'price': f'${p:,}',
                    'beds': bd,
                    'baths': ba,
                    'sqft': sqft if sqft else 'N/A',
                    'year_built': yr,
                    'url': detail,
                    'area': slug.replace('-', ' ').title().replace(' Wa', ', WA'),
                    'source': 'Zillow'
                }
                all_listings.append(entry)
                print(f'  MATCH: {addr} | ${p:,} | {bd}bd/{ba}ba | {sqft}sqft | yr:{yr}')
            elif bd >= 5 and p <= 600000:
                print(f'  NEAR: {addr} | ${p:,} | {bd}bd/{ba}ba | yr:{yr} (baths/year mismatch)')
    except Exception as e:
        print(f'  Error: {e}')

print(f'\n=== TOTAL MATCHING: {len(all_listings)} ===')
for i, l in enumerate(all_listings):
    print(f"{i+1}. {l['address']} | {l['price']} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | Built:{l['year_built']} | {l['url']}")

with open('zillow_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
print('Saved to zillow_results.json')
