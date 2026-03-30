import requests
import json

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
})

all_results = []

# First visit the page to get cookies
page_url = 'https://www.redfin.com/city/19418/WA/Vancouver/filter/property-type=house,min-beds=5,min-baths=2,max-price=600000,min-year-built=2017'
resp = session.get(page_url, timeout=20)
print(f'Page status: {resp.status_code}')

# Now use the API with session cookies
session.headers['Accept'] = 'application/json'
session.headers['Referer'] = page_url

# Search regions: Vancouver WA and surrounding areas
regions = [
    ('Vancouver, WA', '19418', '6'),
    ('Clark County, WA', '360', '5'),  # County level
]

# Also try by zip codes
zip_codes = ['98682', '98683', '98684', '98685', '98686', '98604', '98606', '98607', '98642', '98671']

for name, rid, rtype in regions:
    print(f'\n=== Searching {name} (ID:{rid}, Type:{rtype}) ===')
    try:
        api_url = 'https://www.redfin.com/stingray/api/gis'
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
            'region_id': rid,
            'region_type': rtype,
        }
        api_resp = session.get(api_url, params=params, timeout=15)
        api_text = api_resp.text
        if api_text.startswith('{}&&'):
            api_text = api_text[4:]
        
        if api_resp.status_code == 200:
            api_data = json.loads(api_text)
            homes = api_data.get('payload', {}).get('homes', [])
            print(f'Found {len(homes)} homes')
            
            for h in homes:
                price_val = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else h.get('price', 0)
                beds = h.get('beds', 0)
                baths = h.get('baths', 0)
                sqft_val = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
                year_val = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
                
                # Address
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
                
                print(f'  {full_addr} | ${price_val:,} | {beds}bd/{baths}ba | {sqft_val}sqft | Built {year_val} | MLS#{mls} | {status}')
                print(f'    URL: {url}')
                
                # Filter: 5+ beds, 2.5-3 baths, under $600K, built 2017+
                try:
                    baths_f = float(baths) if baths else 0
                    beds_i = int(beds) if beds else 0
                    year_i = int(year_val) if year_val and year_val != 'N/A' else 0
                    price_i = int(price_val) if price_val else 0
                    
                    if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3 and price_i <= 600000 and year_i >= 2017:
                        all_results.append({
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
                        print(f'    *** MATCHES CRITERIA ***')
                    else:
                        reasons = []
                        if beds_i < 5: reasons.append(f'beds={beds_i}')
                        if baths_f < 2.5 or baths_f > 3: reasons.append(f'baths={baths_f}')
                        if price_i > 600000: reasons.append(f'price=${price_i:,}')
                        if year_i < 2017: reasons.append(f'year={year_i}')
                        print(f'    Does not match: {reasons}')
                except Exception as e:
                    print(f'    Filter error: {e}')
        else:
            print(f'API error: {api_resp.status_code}')
    except Exception as e:
        print(f'Error: {e}')

# Try zip code searches
for zc in zip_codes:
    print(f'\n=== Searching ZIP {zc} ===')
    try:
        # Get region ID for zip code
        auto_resp = session.get('https://www.redfin.com/stingray/do/location-autocomplete',
                               params={'location': zc, 'v': '2'}, timeout=10)
        auto_text = auto_resp.text
        if auto_text.startswith('{}&&'):
            auto_text = auto_text[4:]
        auto_data = json.loads(auto_text)
        
        rid = None
        rtype = None
        if 'payload' in auto_data:
            for section in auto_data['payload'].get('sections', []):
                for row in section.get('rows', []):
                    rid = row.get('id', '')
                    rtype = row.get('type', '')
                    print(f'  ZIP {zc}: ID={rid}, Type={rtype}')
                    break
                if rid:
                    break
        
        if rid:
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
                'region_id': rid,
                'region_type': rtype,
            }
            api_resp = session.get('https://www.redfin.com/stingray/api/gis', params=params, timeout=10)
            api_text = api_resp.text
            if api_text.startswith('{}&&'):
                api_text = api_text[4:]
            
            if api_resp.status_code == 200:
                api_data = json.loads(api_text)
                homes = api_data.get('payload', {}).get('homes', [])
                print(f'  Found {len(homes)} homes')
                
                for h in homes:
                    price_val = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else h.get('price', 0)
                    beds = h.get('beds', 0)
                    baths = h.get('baths', 0)
                    sqft_val = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
                    year_val = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
                    
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
                    
                    # Check if already found
                    if any(r['url'] == url for r in all_results if url):
                        continue
                    
                    try:
                        baths_f = float(baths) if baths else 0
                        beds_i = int(beds) if beds else 0
                        year_i = int(year_val) if year_val and year_val != 'N/A' else 0
                        price_i = int(price_val) if price_val else 0
                        
                        if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3 and price_i <= 600000 and year_i >= 2017:
                            all_results.append({
                                'address': full_addr,
                                'price': f'${price_i:,}',
                                'beds': beds_i,
                                'baths': baths_f,
                                'sqft': sqft_val,
                                'year_built': year_i,
                                'source': 'Redfin',
                                'url': url,
                                'mls': mls,
                                'status': h.get('mlsStatus', 'N/A')
                            })
                            print(f'    *** MATCH: {full_addr} | ${price_i:,} | {beds_i}bd/{baths_f}ba | Built {year_i}')
                    except:
                        pass
    except Exception as e:
        print(f'  ZIP {zc} error: {e}')

print(f'\n\n=========================================')
print(f'TOTAL MATCHING RESULTS: {len(all_results)}')
print(f'=========================================')
for i, r in enumerate(all_results):
    print(f"{i+1}. {r['address']}")
    print(f"   Price: {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']}")
    print(f"   MLS: {r['mls']} | Status: {r['status']}")
    print(f"   URL: {r['url']}")

with open('redfin_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print(f'\nSaved to redfin_results.json')
