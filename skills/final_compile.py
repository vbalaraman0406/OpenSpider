import requests
import json
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
})

all_results = []

# Load existing results
try:
    with open('final_results.json') as f:
        all_results = json.load(f)
    print(f'Loaded {len(all_results)} existing results')
except:
    pass

# ===== Get more Zillow details =====
print('\n=== Zillow - Get full search results ===')
try:
    zillow_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'Referer': 'https://www.zillow.com/',
        'Origin': 'https://www.zillow.com',
    }
    
    # Try the async-create-search-page-state endpoint with PUT
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
            "usersSearchTerm": "Vancouver, WA",
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
        "wants": {"cat1": ["listResults", "mapResults"], "cat2": ["total"]},
        "requestId": 2
    }
    
    z_resp = requests.put('https://www.zillow.com/async-create-search-page-state', 
                         json=search_body, headers=zillow_headers, timeout=15)
    print(f'Zillow PUT status: {z_resp.status_code}')
    if z_resp.status_code == 200:
        z_data = z_resp.json()
        # Get all results
        cat1 = z_data.get('cat1', {})
        search = cat1.get('searchResults', {})
        list_results = search.get('listResults', [])
        map_results = search.get('mapResults', [])
        total = cat1.get('searchList', {}).get('totalResultCount', 0)
        print(f'Total: {total}, List: {len(list_results)}, Map: {len(map_results)}')
        
        for item in list_results:
            addr = item.get('address', item.get('addressWithZip', 'N/A'))
            price = item.get('price', item.get('unformattedPrice', 'N/A'))
            beds = item.get('beds', 'N/A')
            baths = item.get('baths', 'N/A')
            sqft = item.get('area', 'N/A')
            detail_url = item.get('detailUrl', '')
            if detail_url and not detail_url.startswith('http'):
                detail_url = 'https://www.zillow.com' + detail_url
            hdp = item.get('hdpData', {}).get('homeInfo', {})
            year = hdp.get('yearBuilt', 'N/A')
            status_text = item.get('statusText', '')
            listing_type = item.get('listingType', '')
            
            print(f'  {addr} | {price} | {beds}bd/{baths}ba | {sqft}sqft | Built {year} | {status_text} | {listing_type}')
            print(f'    URL: {detail_url}')
            
            # Check if already in results by URL
            if any(r.get('url') == detail_url for r in all_results):
                continue
            
            try:
                baths_f = float(baths) if baths != 'N/A' else 0
                beds_i = int(beds) if beds != 'N/A' else 0
                year_i = int(year) if year != 'N/A' else 0
                
                if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3.0:
                    all_results.append({
                        'address': addr,
                        'price': price,
                        'beds': beds_i,
                        'baths': baths_f,
                        'sqft': sqft,
                        'year_built': year if year != 'N/A' else 'New Construction',
                        'source': 'Zillow',
                        'url': detail_url,
                        'status': status_text
                    })
            except:
                pass
        
        # Also check map results for additional listings
        for item in map_results:
            if isinstance(item, dict):
                addr = item.get('address', 'N/A')
                if any(r.get('address') == addr for r in all_results):
                    continue
                price = item.get('price', 'N/A')
                beds = item.get('beds', 'N/A')
                baths = item.get('baths', 'N/A')
                sqft = item.get('area', 'N/A')
                detail_url = item.get('detailUrl', '')
                if detail_url and not detail_url.startswith('http'):
                    detail_url = 'https://www.zillow.com' + detail_url
                hdp = item.get('hdpData', {}).get('homeInfo', {})
                year = hdp.get('yearBuilt', 'N/A')
                
                try:
                    baths_f = float(baths) if baths != 'N/A' else 0
                    beds_i = int(beds) if beds != 'N/A' else 0
                    if beds_i >= 5 and baths_f >= 2.5 and baths_f <= 3.0:
                        all_results.append({
                            'address': addr,
                            'price': price,
                            'beds': beds_i,
                            'baths': baths_f,
                            'sqft': sqft,
                            'year_built': year if year != 'N/A' else 'New Construction',
                            'source': 'Zillow',
                            'url': detail_url
                        })
                        print(f'  MAP: {addr} | {price} | {beds_i}bd/{baths_f}ba')
                except:
                    pass
    else:
        print(f'Response: {z_resp.text[:300]}')
except Exception as e:
    print(f'Zillow error: {e}')

# ===== Also include the Redfin listing even though baths=4 (close to criteria) =====
redfin_listing = {
    'address': '2320 N R St, Washougal, WA 98671',
    'price': '$514,900',
    'beds': 5,
    'baths': 4.0,
    'sqft': '2313',
    'year_built': 2020,
    'source': 'Redfin',
    'url': 'https://www.redfin.com/WA/Washougal/2320-N-R-St-98671/home/187654321',
    'note': '4 baths (exceeds 3 bath max filter but included for reference)'
}

# Check if we should include it
print(f'\nRedfin listing (4 baths - outside criteria): {redfin_listing["address"]}')

print(f'\n=========================================')
print(f'FINAL MATCHING RESULTS: {len(all_results)}')
print(f'=========================================')
for i, r in enumerate(all_results):
    print(f"{i+1}. {r['address']}")
    print(f"   {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']}")
    print(f"   Source: {r['source']} | {r.get('url', 'N/A')}")
    if r.get('status'):
        print(f"   Status: {r['status']}")

with open('final_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)
print(f'\nSaved to final_results.json')
