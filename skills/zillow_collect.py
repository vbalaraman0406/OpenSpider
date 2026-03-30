import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

areas = [
    ('Vancouver WA', 'vancouver-wa'),
    ('Ridgefield WA', 'ridgefield-wa'),
    ('Battle Ground WA', 'battle-ground-wa'),
    ('Camas WA', 'camas-wa'),
    ('Washougal WA', 'washougal-wa'),
    ('Brush Prairie WA', 'brush-prairie-wa'),
]

all_listings = []
seen_addrs = set()

for area_name, slug in areas:
    url = 'https://www.zillow.com/' + slug + '/houses/'
    print('Fetching: ' + area_name)
    try:
        resp = session.get(url, timeout=30)
        print('  Status: ' + str(resp.status_code))
        if resp.status_code != 200:
            continue
        
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if not match:
            print('  No data found')
            continue
        
        data = json.loads(match.group(1))
        props = data.get('props', {}).get('pageProps', {})
        sp = props.get('searchPageState', {})
        sr = sp.get('cat1', {}).get('searchResults', {})
        results = sr.get('listResults', [])
        print('  Total results: ' + str(len(results)))
        
        for item in results:
            hdp = item.get('hdpData', {}).get('homeInfo', {})
            beds = item.get('beds', hdp.get('bedrooms', 0))
            baths = item.get('baths', hdp.get('bathrooms', 0))
            price_raw = hdp.get('price', item.get('unformattedPrice', 0))
            sqft = item.get('area', hdp.get('livingArea', 'N/A'))
            year = hdp.get('yearBuilt', 0)
            addr = item.get('address', hdp.get('streetAddress', 'N/A'))
            detail = item.get('detailUrl', '')
            if detail and not detail.startswith('http'):
                detail = 'https://www.zillow.com' + detail
            
            try:
                bd = int(beds) if beds else 0
            except:
                bd = 0
            try:
                ba = float(baths) if baths else 0
            except:
                ba = 0
            try:
                p = int(price_raw) if price_raw else 999999
            except:
                p = 999999
            try:
                yr = int(year) if year else 0
            except:
                yr = 0
            
            if bd >= 5 and p <= 600000 and addr not in seen_addrs:
                seen_addrs.add(addr)
                entry = {
                    'address': addr,
                    'price': '$' + '{:,}'.format(p),
                    'beds': bd,
                    'baths': ba,
                    'sqft': sqft if sqft else 'N/A',
                    'year_built': yr if yr > 0 else 'Unknown',
                    'url': detail,
                    'source': 'Zillow',
                    'area': area_name
                }
                all_listings.append(entry)
                print('  FOUND: ' + addr + ' | $' + '{:,}'.format(p) + ' | ' + str(bd) + 'bd/' + str(ba) + 'ba | yr:' + str(yr))
    except Exception as e:
        print('  Error: ' + str(e))

print('')
print('TOTAL 5+BED UNDER 600K: ' + str(len(all_listings)))
for i, l in enumerate(all_listings):
    print(str(i+1) + '. ' + l['address'] + ' | ' + l['price'] + ' | ' + str(l['beds']) + 'bd/' + str(l['baths']) + 'ba | ' + str(l['sqft']) + 'sqft | Built:' + str(l['year_built']) + ' | ' + l['url'])

with open('zillow_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
print('Saved to zillow_results.json')
