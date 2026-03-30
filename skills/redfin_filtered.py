import requests
import json
import warnings
warnings.filterwarnings('ignore')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/'
}

# Search with broader map bounds and more results
url = 'https://www.redfin.com/stingray/api/gis'
params = {
    'al': '3',
    'market': 'portland',
    'num_beds': '5',
    'num_baths': '2',
    'max_price': '600000',
    'min_year_built': '2017',
    'sf': '1,2,3,5,6,7',
    'status': '9',
    'uipt': '1',
    'v': '8',
    'poly': '-122.85 45.55,-122.30 45.55,-122.30 45.85,-122.85 45.85,-122.85 45.55',
    'include_nearby_homes': 'false',
    'num_homes': '500'
}

matching = []

try:
    resp = requests.get(url, params=params, headers=headers, timeout=15, verify=False)
    data = resp.text
    if '&&' in data:
        data = data.split('&&', 1)[1]
    parsed = json.loads(data)
    homes = parsed.get('payload', {}).get('homes', [])
    print(f'Total homes from API: {len(homes)}')
    
    for h in homes:
        def gv(obj, key):
            val = obj.get(key, None)
            if isinstance(val, dict):
                return val.get('value', None)
            return val
        
        price = gv(h, 'price')
        beds = h.get('beds', 0)
        baths = h.get('baths', 0)
        sqft = gv(h, 'sqFt')
        yr = gv(h, 'yearBuilt')
        sl = gv(h, 'streetLine') or ''
        city = h.get('city', '')
        state = h.get('state', '')
        zp = h.get('zip', '')
        lot = gv(h, 'lotSize')
        url_path = h.get('url', '')
        lt = h.get('listingType', '')
        
        # Filter: 5 beds, 2.5+ baths, under $600k, built 2017+
        if beds and beds >= 5 and baths and baths >= 2.5 and price and price <= 600000 and yr and yr >= 2017:
            matching.append({
                'price': price, 'beds': beds, 'baths': baths, 'sqft': sqft,
                'year': yr, 'address': f'{sl}, {city}, {state} {zp}',
                'lot': lot, 'type': lt, 'url': f'https://www.redfin.com{url_path}'
            })
            print(f'MATCH: ${price:,} | {beds}bd/{baths}ba | {sqft}sqft | Built:{yr} | {sl}, {city}, {state} {zp} | Lot:{lot} | https://www.redfin.com{url_path}')
    
    print(f'\nTotal matching: {len(matching)}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

# Also try without include_nearby to see if we get different results
print('\n--- Trying without poly, using region search ---')
# Try Vancouver WA region
for region_id in [19523, 30772, 19524]:
    try:
        params2 = {
            'al': '3',
            'market': 'portland',
            'num_beds': '5',
            'num_baths': '2',
            'max_price': '600000',
            'min_year_built': '2017',
            'sf': '1,2,3,5,6,7',
            'status': '9',
            'uipt': '1',
            'v': '8',
            'region_id': str(region_id),
            'region_type': '6',
            'num_homes': '500'
        }
        resp = requests.get(url, params=params2, headers=headers, timeout=15, verify=False)
        data = resp.text
        if '&&' in data:
            data = data.split('&&', 1)[1]
        parsed = json.loads(data)
        homes = parsed.get('payload', {}).get('homes', [])
        print(f'Region {region_id}: {len(homes)} homes')
        for h in homes:
            def gv2(obj, key):
                val = obj.get(key, None)
                if isinstance(val, dict):
                    return val.get('value', None)
                return val
            price = gv2(h, 'price')
            beds = h.get('beds', 0)
            baths = h.get('baths', 0)
            yr = gv2(h, 'yearBuilt')
            sqft = gv2(h, 'sqFt')
            sl = gv2(h, 'streetLine') or ''
            city = h.get('city', '')
            state = h.get('state', '')
            zp = h.get('zip', '')
            url_path = h.get('url', '')
            lot = gv2(h, 'lotSize')
            if beds and beds >= 5 and baths and baths >= 2.5 and price and price <= 600000 and yr and yr >= 2017:
                print(f'  MATCH: ${price:,} | {beds}bd/{baths}ba | {sqft}sqft | Built:{yr} | {sl}, {city}, {state} {zp} | https://www.redfin.com{url_path}')
    except Exception as e:
        print(f'  Region {region_id} error: {e}')
