import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
})

# Visit page for cookies
resp = session.get('https://www.redfin.com/city/19418/WA/Vancouver', timeout=20)
print(f'Page: {resp.status_code}')

session.headers['Accept'] = 'application/json'
session.headers['Referer'] = 'https://www.redfin.com/city/19418/WA/Vancouver'

api_url = 'https://www.redfin.com/stingray/api/gis'

# Use poly for Vancouver WA area
params = {
    'al': '1',
    'num_beds': '5',
    'num_baths': '2',
    'max_price': '600000',
    'min_year_built': '2017',
    'sf': '1,2,5,6,7',
    'status': '9',
    'uipt': '1',
    'v': '8',
    'market': 'portland',
    'poly': '-122.90 45.50,-122.20 45.50,-122.20 45.90,-122.90 45.90,-122.90 45.50',
}

api_resp = session.get(api_url, params=params, timeout=15)
api_text = api_resp.text
if api_text.startswith('{}&&'):
    api_text = api_text[4:]

print(f'API: {api_resp.status_code}')
api_data = json.loads(api_text)
homes = api_data.get('payload', {}).get('homes', [])
print(f'Total homes: {len(homes)}')

target_cities = ['vancouver', 'ridgefield', 'battle ground', 'camas', 'washougal', 'brush prairie', 'la center', 'hockinson']
matching = []

for h in homes:
    price_info = h.get('price', {})
    price_val = price_info.get('value', 0) if isinstance(price_info, dict) else (price_info if isinstance(price_info, (int, float)) else 0)
    beds = h.get('beds', 0)
    baths = h.get('baths', 0)
    sqft_info = h.get('sqFt', {})
    sqft_val = sqft_info.get('value', 'N/A') if isinstance(sqft_info, dict) else sqft_info
    year_info = h.get('yearBuilt', {})
    year_val = year_info.get('value', 'N/A') if isinstance(year_info, dict) else year_info
    
    sl = h.get('streetLine', {})
    street = sl.get('value', str(sl)) if isinstance(sl, dict) else str(sl)
    city = h.get('city', '')
    state = h.get('state', '')
    zipcode = h.get('zip', '')
    full_addr = f"{street}, {city}, {state} {zipcode}"
    
    url = h.get('url', '')
    if url and not url.startswith('http'):
        url = 'https://www.redfin.com' + url
    
    mls = h.get('mlsId', {}).get('value', 'N/A') if isinstance(h.get('mlsId'), dict) else 'N/A'
    status = h.get('mlsStatus', 'N/A')
    
    try:
        baths_f = float(baths) if baths else 0
        beds_i = int(beds) if beds else 0
        year_i = int(year_val) if year_val and year_val != 'N/A' else 0
        price_i = int(price_val) if price_val else 0
    except:
        continue
    
    print(f'{full_addr} | ${price_i:,} | {beds_i}bd/{baths_f}ba | {sqft_val}sqft | Built {year_i} | {status}')
    
    # Check criteria: 5+ beds, 2.5-3 baths, <=600K, built 2017+
    if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3.0 and price_i <= 600000 and year_i >= 2017:
        matching.append({
            'address': full_addr,
            'price': f'${price_i:,}',
            'beds': beds_i,
            'baths': baths_f,
            'sqft': sqft_val,
            'year_built': year_i,
            'source': 'Redfin',
            'url': url,
            'mls': mls,
            'status': status
        })
        print(f'  *** MATCH ***')

print(f'\n=== MATCHING: {len(matching)} ===')
for i, r in enumerate(matching):
    print(f"{i+1}. {r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']} | {r['url']}")

# Also try with relaxed baths (min 2) to see what's available
print(f'\n=== ALL 5+ bed homes under $600K built 2017+ (any baths) ===')
for h in homes:
    price_info = h.get('price', {})
    price_val = price_info.get('value', 0) if isinstance(price_info, dict) else (price_info if isinstance(price_info, (int, float)) else 0)
    beds = h.get('beds', 0)
    baths = h.get('baths', 0)
    year_info = h.get('yearBuilt', {})
    year_val = year_info.get('value', 'N/A') if isinstance(year_info, dict) else year_info
    sl = h.get('streetLine', {})
    street = sl.get('value', str(sl)) if isinstance(sl, dict) else str(sl)
    city = h.get('city', '')
    
    try:
        beds_i = int(beds) if beds else 0
        year_i = int(year_val) if year_val and year_val != 'N/A' else 0
        price_i = int(price_val) if price_val else 0
        baths_f = float(baths) if baths else 0
        if beds_i >= 5 and price_i <= 600000 and year_i >= 2017:
            print(f'  {street}, {city} | ${price_i:,} | {beds_i}bd/{baths_f}ba | Built {year_i}')
    except:
        pass

with open('redfin_results.json', 'w') as f:
    json.dump(matching, f, indent=2)
print(f'\nSaved {len(matching)} results')
