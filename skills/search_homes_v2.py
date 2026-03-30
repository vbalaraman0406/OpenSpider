import requests
import json
import csv
import io
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

results = []

# ===== REDFIN STINGRAY API =====
print('=== Redfin Stingray API ===')
try:
    # First, get the correct region info
    session = requests.Session()
    session.headers.update(headers)
    
    # Get region ID
    auto_resp = session.get('https://www.redfin.com/stingray/do/location-autocomplete', 
                           params={'location': 'Vancouver, WA', 'v': '2'}, timeout=15)
    print(f'Autocomplete status: {auto_resp.status_code}')
    auto_text = auto_resp.text
    if auto_text.startswith('{}&&'):
        auto_text = auto_text[4:]
    auto_data = json.loads(auto_text)
    
    region_id = None
    region_type = None
    if 'payload' in auto_data:
        for section in auto_data['payload'].get('sections', []):
            for row in section.get('rows', []):
                name = row.get('name', '')
                if 'Vancouver' in name:
                    region_id = row.get('id', '')
                    region_type = row.get('type', '')
                    print(f'Region: {name}, ID: {region_id}, Type: {region_type}')
                    break
            if region_id:
                break
    
    if not region_id:
        # Fallback region IDs for Vancouver WA
        region_id = '19418'
        region_type = '6'
        print(f'Using fallback region_id: {region_id}')
    
    # Try the gis endpoint
    gis_url = 'https://www.redfin.com/stingray/api/gis'
    gis_params = {
        'al': '1',
        'min_stories': '1',
        'num_beds': '5',
        'num_baths': '2',
        'max_price': '600000',
        'min_year_built': '2017',
        'sf': '1,2,5,6,7',
        'status': '9',
        'uipt': '1',
        'v': '8',
        'region_id': region_id,
        'region_type': region_type,
    }
    
    gis_resp = session.get(gis_url, params=gis_params, timeout=15)
    print(f'GIS status: {gis_resp.status_code}')
    gis_text = gis_resp.text
    if gis_text.startswith('{}&&'):
        gis_text = gis_text[4:]
    
    if gis_resp.status_code == 200:
        gis_data = json.loads(gis_text)
        homes = gis_data.get('payload', {}).get('homes', [])
        print(f'Found {len(homes)} homes from Redfin GIS')
        
        for home in homes:
            mlsid = home.get('mlsId', {})
            price_info = home.get('price', {})
            beds = home.get('beds', 'N/A')
            baths = home.get('baths', 'N/A')
            sqft = home.get('sqFt', 'N/A')
            year = home.get('yearBuilt', 'N/A')
            url = home.get('url', '')
            
            # Build address
            addr_parts = []
            if home.get('streetLine', {}).get('value'):
                addr_parts.append(home['streetLine']['value'])
            elif home.get('streetLine'):
                addr_parts.append(str(home['streetLine']))
            
            city = home.get('city', '')
            state = home.get('state', '')
            zipcode = home.get('zip', '')
            
            full_addr = f"{', '.join(addr_parts)}, {city}, {state} {zipcode}".strip(', ')
            if not full_addr or full_addr == ', , ':
                full_addr = home.get('streetLine', 'Unknown')
            
            price_val = price_info.get('value', 'N/A') if isinstance(price_info, dict) else price_info
            
            if not url.startswith('http') and url:
                url = 'https://www.redfin.com' + url
            
            # Filter baths <= 3
            try:
                if float(baths) > 3:
                    continue
            except:
                pass
            
            results.append({
                'address': full_addr,
                'price': f'${price_val:,}' if isinstance(price_val, (int, float)) else str(price_val),
                'beds': beds,
                'baths': baths,
                'sqft': sqft,
                'year_built': year,
                'source': 'Redfin',
                'url': url
            })
    else:
        print(f'GIS response: {gis_text[:500]}')

except Exception as e:
    print(f'Redfin error: {e}')
    import traceback
    traceback.print_exc()

# ===== Try broader area with multiple cities =====
print('\n=== Redfin Broader Area Search ===')
cities = [
    ('Ridgefield, WA', None),
    ('Battle Ground, WA', None),
    ('Camas, WA', None),
    ('Washougal, WA', None),
    ('Brush Prairie, WA', None),
]

for city_name, _ in cities:
    try:
        auto_resp = session.get('https://www.redfin.com/stingray/do/location-autocomplete',
                               params={'location': city_name, 'v': '2'}, timeout=10)
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
                    print(f'{city_name}: ID={rid}, Type={rtype}')
                    break
                if rid:
                    break
        
        if rid:
            gis_params2 = gis_params.copy()
            gis_params2['region_id'] = rid
            gis_params2['region_type'] = rtype
            
            gis_resp2 = session.get(gis_url, params=gis_params2, timeout=10)
            gis_text2 = gis_resp2.text
            if gis_text2.startswith('{}&&'):
                gis_text2 = gis_text2[4:]
            
            if gis_resp2.status_code == 200:
                gis_data2 = json.loads(gis_text2)
                homes2 = gis_data2.get('payload', {}).get('homes', [])
                print(f'  {city_name}: {len(homes2)} homes')
                
                for home in homes2:
                    beds = home.get('beds', 'N/A')
                    baths = home.get('baths', 'N/A')
                    sqft = home.get('sqFt', 'N/A')
                    year = home.get('yearBuilt', 'N/A')
                    url = home.get('url', '')
                    price_info = home.get('price', {})
                    price_val = price_info.get('value', 'N/A') if isinstance(price_info, dict) else price_info
                    
                    sl = home.get('streetLine', {})
                    street = sl.get('value', str(sl)) if isinstance(sl, dict) else str(sl)
                    city = home.get('city', '')
                    state = home.get('state', '')
                    zipcode = home.get('zip', '')
                    full_addr = f"{street}, {city}, {state} {zipcode}"
                    
                    if not url.startswith('http') and url:
                        url = 'https://www.redfin.com' + url
                    
                    # Check if already in results
                    if any(r['url'] == url for r in results if url):
                        continue
                    
                    try:
                        if float(baths) > 3:
                            continue
                    except:
                        pass
                    
                    results.append({
                        'address': full_addr,
                        'price': f'${price_val:,}' if isinstance(price_val, (int, float)) else str(price_val),
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year_built': year,
                        'source': 'Redfin',
                        'url': url
                    })
    except Exception as e:
        print(f'  {city_name} error: {e}')

# ===== REALTOR.COM API =====
print('\n=== Realtor.com Search ===')
try:
    realtor_url = 'https://www.realtor.com/api/v1/hulk'
    realtor_params = {
        'client_id': 'rdc-x',
        'schema': 'vesta'
    }
    realtor_body = {
        'query': """{\n  home_search(\n    query: {\n      status: \"for_sale\"\n      primary: true\n      search_location: {location: \"Vancouver, WA\"}\n    }\n    limit: 50\n    sort: [{field: \"list_date\", direction: \"desc\"}]\n  ) {\n    total\n    results {\n      property_id\n      list_price\n      description {\n        beds\n        baths\n        sqft\n        year_built\n      }\n      location {\n        address {\n          line\n          city\n          state_code\n          postal_code\n        }\n      }\n      href\n    }\n  }\n}"""
    }
    realtor_headers = headers.copy()
    realtor_headers['Content-Type'] = 'application/json'
    
    resp = session.post(realtor_url, json=realtor_body, headers=realtor_headers, timeout=15)
    print(f'Realtor.com status: {resp.status_code}')
    if resp.status_code == 200:
        rdata = resp.json()
        homes_r = rdata.get('data', {}).get('home_search', {}).get('results', [])
        print(f'Realtor.com results: {len(homes_r)}')
        for h in homes_r:
            desc = h.get('description', {})
            beds = desc.get('beds', 0)
            baths = desc.get('baths', 0)
            sqft = desc.get('sqft', 'N/A')
            year = desc.get('year_built', 0)
            price = h.get('list_price', 0)
            loc = h.get('location', {}).get('address', {})
            addr = f"{loc.get('line','')}, {loc.get('city','')}, {loc.get('state_code','')} {loc.get('postal_code','')}"
            href = h.get('href', '')
            if href and not href.startswith('http'):
                href = 'https://www.realtor.com' + href
            
            # Apply filters
            if beds >= 5 and baths >= 2.5 and baths <= 3 and price <= 600000 and year >= 2017:
                results.append({
                    'address': addr,
                    'price': f'${price:,}',
                    'beds': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'year_built': year,
                    'source': 'Realtor.com',
                    'url': href
                })
    else:
        print(f'Realtor response: {resp.text[:300]}')
except Exception as e:
    print(f'Realtor.com error: {e}')

print(f'\n=== TOTAL RESULTS: {len(results)} ===')
for i, r in enumerate(results):
    print(f"{i+1}. {r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']} | {r['source']} | {r['url']}")

with open('search_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nResults saved to search_results.json')
