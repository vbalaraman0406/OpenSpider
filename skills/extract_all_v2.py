import requests
import json
import re
import csv
import io

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
})

all_results = []

# Visit Redfin for cookies
resp = session.get('https://www.redfin.com/', timeout=20)

# ===== REDFIN CSV - Broader search (relax baths to 2) =====
print('=== Redfin CSV - All 5+ bed homes ===')
session.headers['Referer'] = 'https://www.redfin.com/'
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

if csv_resp.status_code == 200:
    full_csv = csv_resp.text
    print(f'Full CSV content:')
    print(full_csv)
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(full_csv))
    for row in reader:
        addr = row.get('ADDRESS', '')
        if not addr or 'In accordance' in addr:
            continue
        city = row.get('CITY', '')
        state = row.get('STATE OR PROVINCE', '')
        zipcode = row.get('ZIP OR POSTAL CODE', '')
        price = row.get('PRICE', '')
        beds = row.get('BEDS', '')
        baths = row.get('BATHS', '')
        sqft = row.get('SQUARE FEET', '')
        year = row.get('YEAR BUILT', '')
        url = row.get('URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)', '')
        if not url:
            # Try other URL column names
            for k in row.keys():
                if 'URL' in k.upper():
                    url = row[k]
                    break
        status = row.get('STATUS', '')
        
        full_addr = f"{addr}, {city}, {state} {zipcode}"
        print(f'\nParsed: {full_addr} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | Built {year} | {status}')
        print(f'URL: {url}')
        
        try:
            baths_f = float(baths)
            if baths_f >= 2.5 and baths_f <= 3.0:
                all_results.append({
                    'address': full_addr,
                    'price': f'${price}' if not price.startswith('$') else price,
                    'beds': int(beds),
                    'baths': baths_f,
                    'sqft': sqft,
                    'year_built': year,
                    'source': 'Redfin',
                    'url': url,
                    'status': status
                })
                print('  *** MATCHES 2.5-3 bath criteria ***')
            else:
                print(f'  Baths {baths_f} outside 2.5-3 range')
        except:
            pass

# ===== Try Zillow with different approach =====
print('\n=== Zillow - Try fetching search data ===')
try:
    # Zillow's page title said "4 Homes For Sale" - let's try to get those
    # Try the Zillow search API with different endpoint
    zillow_api_url = 'https://www.zillow.com/async-create-search-page-state'
    zillow_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zillow.com/',
        'Origin': 'https://www.zillow.com',
    }
    
    search_body = {
        "searchQueryState": {
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
        },
        "wants": {"cat1": ["listResults", "mapResults"]},
        "requestId": 1
    }
    
    z_resp = requests.put(zillow_api_url, json=search_body, headers=zillow_headers, timeout=15)
    print(f'Zillow API status: {z_resp.status_code}')
    if z_resp.status_code == 200:
        z_data = z_resp.json()
        list_results = z_data.get('cat1', {}).get('searchResults', {}).get('listResults', [])
        map_results = z_data.get('cat1', {}).get('searchResults', {}).get('mapResults', [])
        print(f'List: {len(list_results)}, Map: {len(map_results)}')
        
        for item in list_results + map_results:
            addr = item.get('address', 'N/A')
            price = item.get('price', item.get('unformattedPrice', 'N/A'))
            beds = item.get('beds', 'N/A')
            baths = item.get('baths', 'N/A')
            sqft = item.get('area', 'N/A')
            detail_url = item.get('detailUrl', '')
            if detail_url and not detail_url.startswith('http'):
                detail_url = 'https://www.zillow.com' + detail_url
            hdp = item.get('hdpData', {}).get('homeInfo', {})
            year = hdp.get('yearBuilt', 'N/A')
            
            print(f'  Zillow: {addr} | {price} | {beds}bd/{baths}ba | {sqft}sqft | Built {year}')
            
            # Check if already in results
            if any(r['address'] == addr for r in all_results):
                continue
            
            try:
                baths_f = float(baths) if baths != 'N/A' else 0
                if baths_f >= 2.5 and baths_f <= 3.0:
                    all_results.append({
                        'address': addr,
                        'price': price,
                        'beds': beds,
                        'baths': baths_f,
                        'sqft': sqft,
                        'year_built': year,
                        'source': 'Zillow',
                        'url': detail_url
                    })
            except:
                pass
    else:
        print(f'Zillow response: {z_resp.text[:300]}')
except Exception as e:
    print(f'Zillow API error: {e}')

# ===== Try Realtor.com =====
print('\n=== Realtor.com Search ===')
try:
    # Try realtor.com search page
    realtor_url = 'https://www.realtor.com/realestateandhomes-search/Vancouver_WA/beds-5/baths-2/price-na-600000/age-8/type-single-family-home'
    r_resp = session.get(realtor_url, timeout=15)
    print(f'Realtor.com status: {r_resp.status_code}, length: {len(r_resp.text)}')
    
    if r_resp.status_code == 200:
        # Look for __NEXT_DATA__
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r_resp.text)
        if m:
            next_data = json.loads(m.group(1))
            props = next_data.get('props', {}).get('pageProps', {})
            # Navigate to search results
            search_results = props.get('searchResults', props.get('properties', []))
            if isinstance(search_results, dict):
                home_search = search_results.get('home_search', {})
                results_list = home_search.get('results', [])
                total = home_search.get('total', 0)
                print(f'Realtor.com: {len(results_list)} results, total: {total}')
                
                for h in results_list:
                    desc = h.get('description', {})
                    loc = h.get('location', {}).get('address', {})
                    addr = f"{loc.get('line', '')}, {loc.get('city', '')}, {loc.get('state_code', '')} {loc.get('postal_code', '')}"
                    price = h.get('list_price', 0)
                    beds = desc.get('beds', 0)
                    baths = desc.get('baths', 0)
                    sqft = desc.get('sqft', 'N/A')
                    year = desc.get('year_built', 0)
                    href = h.get('href', '')
                    if href and not href.startswith('http'):
                        href = 'https://www.realtor.com' + href
                    
                    print(f'  {addr} | ${price:,} | {beds}bd/{baths}ba | {sqft}sqft | Built {year}')
                    
                    try:
                        if beds >= 5 and baths >= 2.5 and baths <= 3.0 and price <= 600000 and year >= 2017:
                            if not any(r['address'] == addr for r in all_results):
                                all_results.append({
                                    'address': addr,
                                    'price': f'${price:,}',
                                    'beds': beds,
                                    'baths': baths,
                                    'sqft': sqft,
                                    'year_built': year,
                                    'source': 'Realtor.com',
                                    'url': href
                                })
                                print(f'    *** MATCH ***')
                    except:
                        pass
            else:
                print(f'Search results type: {type(search_results)}')
                # Try to find keys
                print(f'Props keys: {list(props.keys())[:10]}')
        else:
            print('No __NEXT_DATA__ found')
            # Check for other data patterns
            title_m = re.search(r'<title>(.*?)</title>', r_resp.text)
            if title_m:
                print(f'Title: {title_m.group(1)}')
except Exception as e:
    print(f'Realtor.com error: {e}')

print(f'\n=========================================')
print(f'TOTAL MATCHING RESULTS: {len(all_results)}')
print(f'=========================================')
for i, r in enumerate(all_results):
    print(f"{i+1}. {r['address']}")
    print(f"   {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']}")
    print(f"   Source: {r['source']} | {r['url']}")

with open('final_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print(f'\nSaved to final_results.json')
