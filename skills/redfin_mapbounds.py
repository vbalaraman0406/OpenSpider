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
    'Upgrade-Insecure-Requests': '1',
})

# First visit page to get cookies
page_url = 'https://www.redfin.com/city/19418/WA/Vancouver'
resp = session.get(page_url, timeout=20)
print(f'Page status: {resp.status_code}')

# Now use API with map bounds for Vancouver WA area
# Vancouver WA: lat ~45.63, lng ~-122.67
# Broader area including Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie
# North: ~45.85 (Ridgefield/Battle Ground)
# South: ~45.55
# West: ~-122.85
# East: ~-122.25 (Camas/Washougal)

session.headers['Accept'] = 'application/json'
session.headers['Referer'] = page_url

api_url = 'https://www.redfin.com/stingray/api/gis'
params = {
    'al': '1',
    'num_beds': '5',
    'num_baths': '2',
    'max_price': '600000',
    'min_year_built': '2017',
    'sf': '1,2,5,6,7',
    'status': '9',
    'uipt': '1',  # 1 = house
    'v': '8',
    'market': 'portland',
    'lat_min': '45.50',
    'lat_max': '45.90',
    'lng_min': '-122.90',
    'lng_max': '-122.20',
}

print('\n=== Redfin Map Bounds Search ===')
try:
    api_resp = session.get(api_url, params=params, timeout=15)
    api_text = api_resp.text
    if api_text.startswith('{}&&'):
        api_text = api_text[4:]
    
    print(f'API status: {api_resp.status_code}')
    if api_resp.status_code == 200:
        api_data = json.loads(api_text)
        homes = api_data.get('payload', {}).get('homes', [])
        print(f'Found {len(homes)} homes')
        
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
            
            lat = h.get('latLong', {}).get('value', {}).get('latitude', 0) if isinstance(h.get('latLong'), dict) else 0
            lng = h.get('latLong', {}).get('value', {}).get('longitude', 0) if isinstance(h.get('latLong'), dict) else 0
            mls = h.get('mlsId', {}).get('value', 'N/A') if isinstance(h.get('mlsId'), dict) else 'N/A'
            status = h.get('mlsStatus', 'N/A')
            
            print(f'  {full_addr} | ${price_val:,} | {beds}bd/{baths}ba | {sqft_val}sqft | Built {year_val} | lat:{lat:.4f} lng:{lng:.4f}')
            
            # Verify it's in WA state (lat > 45.5, lng < -122)
            try:
                if lat > 45.4 and lat < 46.0 and lng < -122.0 and lng > -123.0:
                    baths_f = float(baths) if baths else 0
                    beds_i = int(beds) if beds else 0
                    year_i = int(year_val) if year_val and year_val != 'N/A' else 0
                    price_i = int(price_val) if price_val else 0
                    
                    if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3 and price_i <= 600000 and year_i >= 2017:
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
                        print(f'    *** MATCHES ***')
                else:
                    print(f'    Outside WA area')
            except:
                pass
        
        print(f'\n=== MATCHING RESULTS: {len(matching)} ===')
        for i, r in enumerate(matching):
            print(f"{i+1}. {r['address']}")
            print(f"   {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']}")
            print(f"   URL: {r['url']}")
        
        with open('redfin_results.json', 'w') as f:
            json.dump(matching, f, indent=2)
    else:
        print(f'Error: {api_text[:500]}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

# Also try without region_id, just map bounds
print('\n=== Try with poly parameter ===')
try:
    params2 = params.copy()
    # Remove lat/lng and try with poly (polygon)
    # Vancouver WA area polygon
    del params2['lat_min']
    del params2['lat_max']
    del params2['lng_min']
    del params2['lng_max']
    params2['poly'] = '-122.90 45.50,-122.20 45.50,-122.20 45.90,-122.90 45.90,-122.90 45.50'
    
    api_resp2 = session.get(api_url, params=params2, timeout=15)
    api_text2 = api_resp2.text
    if api_text2.startswith('{}&&'):
        api_text2 = api_text2[4:]
    print(f'Poly API status: {api_resp2.status_code}')
    if api_resp2.status_code == 200:
        api_data2 = json.loads(api_text2)
        homes2 = api_data2.get('payload', {}).get('homes', [])
        print(f'Poly search found {len(homes2)} homes')
        for h in homes2[:5]:
            sl = h.get('streetLine', {})
            street = sl.get('value', str(sl)) if isinstance(sl, dict) else str(sl)
            city = h.get('city', '')
            state = h.get('state', '')
            print(f'  {street}, {city}, {state}')
    else:
        print(f'Poly error: {api_text2[:300]}')
except Exception as e:
    print(f'Poly error: {e}')
