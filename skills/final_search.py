import requests
import json
import re
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
})

all_results = []

# ===== REDFIN - Try with correct Vancouver WA coordinates =====
print('=== Redfin Search with correct coords ===')
# Vancouver WA proper: 45.6387, -122.6615
# Broader area: Ridgefield (45.815, -122.742), Battle Ground (45.781, -122.534)
# Camas (45.587, -122.399), Washougal (45.583, -122.353)
# Brush Prairie (45.733, -122.548)

# Visit Redfin first
resp = session.get('https://www.redfin.com/', timeout=20)
print(f'Redfin home: {resp.status_code}')

session.headers['Accept'] = 'application/json'
session.headers['Referer'] = 'https://www.redfin.com/'

# Try the gis-csv endpoint which might work better
print('\n--- Redfin GIS-CSV ---')
try:
    csv_url = 'https://www.redfin.com/stingray/api/gis-csv'
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
        'poly': '-122.85 45.55,-122.25 45.55,-122.25 45.85,-122.85 45.85,-122.85 45.55',
    }
    csv_resp = session.get(csv_url, params=params, timeout=15)
    print(f'CSV status: {csv_resp.status_code}, length: {len(csv_resp.text)}')
    if csv_resp.status_code == 200 and len(csv_resp.text) > 100:
        lines = csv_resp.text.strip().split('\n')
        print(f'CSV lines: {len(lines)}')
        if len(lines) > 1:
            headers_csv = lines[0]
            print(f'Headers: {headers_csv[:200]}')
            for line in lines[1:5]:
                print(f'Row: {line[:200]}')
    else:
        print(f'CSV response: {csv_resp.text[:300]}')
except Exception as e:
    print(f'CSV error: {e}')

# Try GIS API with correct polygon
print('\n--- Redfin GIS API ---')
try:
    gis_url = 'https://www.redfin.com/stingray/api/gis'
    params_gis = {
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
        'poly': '-122.85 45.55,-122.25 45.55,-122.25 45.85,-122.85 45.85,-122.85 45.55',
    }
    gis_resp = session.get(gis_url, params=params_gis, timeout=15)
    gis_text = gis_resp.text
    if gis_text.startswith('{}&&'):
        gis_text = gis_text[4:]
    print(f'GIS status: {gis_resp.status_code}')
    if gis_resp.status_code == 200:
        gis_data = json.loads(gis_text)
        homes = gis_data.get('payload', {}).get('homes', [])
        total = gis_data.get('payload', {}).get('totalResultCount', 0)
        print(f'Homes: {len(homes)}, Total: {total}')
        
        for h in homes:
            price_info = h.get('price', {})
            price_val = price_info.get('value', 0) if isinstance(price_info, dict) else price_info
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
            url = h.get('url', '')
            if url and not url.startswith('http'):
                url = 'https://www.redfin.com' + url
            lat = 0
            lng = 0
            ll = h.get('latLong', {})
            if isinstance(ll, dict):
                llv = ll.get('value', {})
                if isinstance(llv, dict):
                    lat = llv.get('latitude', 0)
                    lng = llv.get('longitude', 0)
            
            full_addr = f"{street}, {city}, {state} {zipcode}"
            print(f'  {full_addr} | ${price_val:,} | {beds}bd/{baths}ba | {sqft_val}sqft | Built {year_val} | lat:{lat} lng:{lng}')
            
            try:
                beds_i = int(beds) if beds else 0
                baths_f = float(baths) if baths else 0
                year_i = int(year_val) if year_val and year_val != 'N/A' else 0
                price_i = int(price_val) if price_val else 0
                if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3.0 and price_i <= 600000 and year_i >= 2017:
                    all_results.append({
                        'address': full_addr,
                        'price': f'${price_i:,}',
                        'beds': beds_i,
                        'baths': baths_f,
                        'sqft': sqft_val,
                        'year_built': year_i,
                        'source': 'Redfin',
                        'url': url
                    })
                    print(f'    *** MATCH ***')
            except:
                pass
    else:
        print(f'GIS error: {gis_text[:300]}')
except Exception as e:
    print(f'GIS error: {e}')

# ===== ZILLOW - Try with proper API =====
print('\n=== Zillow Search ===')
try:
    # Try Zillow's search results page and extract embedded data
    zillow_headers = session.headers.copy()
    zillow_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    zillow_headers['Referer'] = 'https://www.google.com/'
    
    # Use a search URL that includes all our filters
    search_state = json.dumps({
        "pagination": {},
        "isMapVisible": True,
        "mapBounds": {
            "north": 45.85,
            "south": 45.55,
            "east": -122.25,
            "west": -122.85
        },
        "filterState": {
            "beds": {"min": 5},
            "baths": {"min": 2},
            "price": {"max": 600000},
            "built": {"min": "2017"},
            "tow": {"value": False},
            "mf": {"value": False},
            "con": {"value": False},
            "land": {"value": False},
            "apa": {"value": False},
            "manu": {"value": False}
        },
        "isListVisible": True
    })
    
    zillow_url = f'https://www.zillow.com/homes/for_sale/?searchQueryState={requests.utils.quote(search_state)}'
    z_resp = session.get(zillow_url, headers=zillow_headers, timeout=15, allow_redirects=True)
    print(f'Zillow status: {z_resp.status_code}, URL: {z_resp.url[:100]}, length: {len(z_resp.text)}')
    
    if z_resp.status_code == 200 and len(z_resp.text) > 10000:
        # Look for embedded search results
        # Zillow embeds data in various script tags
        patterns_to_try = [
            r'"listResults"\s*:\s*(\[.*?\])\s*,\s*"',
            r'"searchResults"\s*:\s*({.*?})\s*,\s*"',
            r'"cat1"\s*:\s*({.*?})\s*\}',
            r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        ]
        for p in patterns_to_try:
            m = re.search(p, z_resp.text[:200000], re.DOTALL)
            if m:
                print(f'Found pattern: {p[:30]}...')
                snippet = m.group(1)[:500]
                print(f'Snippet: {snippet}')
                break
        else:
            print('No Zillow data patterns found')
            if 'captcha' in z_resp.text.lower():
                print('CAPTCHA detected')
            # Check title
            title_m = re.search(r'<title>(.*?)</title>', z_resp.text)
            if title_m:
                print(f'Page title: {title_m.group(1)}')
except Exception as e:
    print(f'Zillow error: {e}')

print(f'\n=== FINAL RESULTS: {len(all_results)} ===')
for i, r in enumerate(all_results):
    print(f"{i+1}. {r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']} | {r['url']}")

with open('final_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
