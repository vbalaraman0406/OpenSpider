import requests
import json
import re
import urllib.parse

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

areas = [
    ('Vancouver WA', 27445, 6),
    ('Ridgefield WA', 53294, 6),
    ('Battle Ground WA', 4547, 6),
    ('Camas WA', 8816, 6),
    ('Washougal WA', 52685, 6),
]

all_listings = []

for area_name, region_id, region_type in areas:
    search_state = {
        'pagination': {},
        'isMapVisible': False,
        'filterState': {
            'sort': {'value': 'days'},
            'beds': {'min': 5},
            'baths': {'min': 2},
            'price': {'max': 600000},
            'con': {'value': False},
            'mf': {'value': False},
            'land': {'value': False},
            'tow': {'value': False},
            'apa': {'value': False},
            'manu': {'value': False},
        },
        'isListVisible': True,
        'regionSelection': [{'regionId': region_id, 'regionType': region_type}],
    }
    
    encoded = urllib.parse.quote(json.dumps(search_state))
    slug = area_name.lower().replace(' ', '-')
    url = f'https://www.zillow.com/{slug}/houses/?searchQueryState={encoded}'
    
    print(f'Fetching: {area_name}')
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f'  Status: {resp.status_code}')
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if match:
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
                
                if bd >= 5 and p <= 600000:
                    entry = {
                        'address': addr,
                        'price': f'${p:,}',
                        'beds': bd,
                        'baths': ba,
                        'sqft': sqft,
                        'year_built': yr if yr > 0 else 'N/A',
                        'url': detail,
                        'area': area_name,
                        'source': 'Zillow'
                    }
                    all_listings.append(entry)
                    print(f'  FOUND: {addr} | ${p:,} | {bd}bd/{ba}ba | {sqft}sqft | yr:{yr}')
        else:
            print(f'  No data found')
    except Exception as e:
        print(f'  Error: {e}')

print(f'\n=== TOTAL FOUND: {len(all_listings)} ===')
for i, l in enumerate(all_listings):
    print(f"{i+1}. {l['address']} | {l['price']} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | Built:{l['year_built']} | {l['url']}")

with open('zillow_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
print('Saved to zillow_results.json')
