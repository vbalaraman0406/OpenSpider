import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Try multiple areas
areas = [
    ('Vancouver WA', 'vancouver-wa'),
    ('Ridgefield WA', 'ridgefield-wa'),
    ('Battle Ground WA', 'battle-ground-wa'),
    ('Camas WA', 'camas-wa'),
    ('Washougal WA', 'washougal-wa'),
]

all_listings = []

for area_name, area_slug in areas:
    url = f'https://www.zillow.com/{area_slug}/houses/5-_beds/2-_baths/0-600000_price/'
    print(f'Fetching: {area_name} -> {url}')
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f'  Status: {resp.status_code}, Length: {len(resp.text)}')
        
        # Look for embedded search results JSON
        # Zillow embeds data in a script tag with id="__NEXT_DATA__"
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', resp.text)
        if match:
            data = json.loads(match.group(1))
            # Navigate the JSON structure to find listings
            props = data.get('props', {}).get('pageProps', {})
            search_results = props.get('searchPageState', {}).get('cat1', {}).get('searchResults', {})
            list_results = search_results.get('listResults', [])
            map_results = search_results.get('mapResults', [])
            print(f'  List results: {len(list_results)}, Map results: {len(map_results)}')
            
            results = list_results if list_results else map_results
            for item in results:
                hdp = item.get('hdpData', {}).get('homeInfo', {})
                addr = item.get('address', hdp.get('streetAddress', 'N/A'))
                price = item.get('price', hdp.get('price', 'N/A'))
                beds = item.get('beds', hdp.get('bedrooms', 'N/A'))
                baths = item.get('baths', hdp.get('bathrooms', 'N/A'))
                sqft = item.get('area', hdp.get('livingArea', 'N/A'))
                year = hdp.get('yearBuilt', 'N/A')
                detail = item.get('detailUrl', '')
                if detail and not detail.startswith('http'):
                    detail = 'https://www.zillow.com' + detail
                
                # Filter: 5+ beds, 2.5-3 baths, under 600K, built 2017+
                try:
                    b = float(baths) if baths != 'N/A' else 0
                    bd = int(beds) if beds != 'N/A' else 0
                    p = float(str(price).replace('$','').replace(',','').replace('+','')) if price != 'N/A' else 999999
                    yr = int(year) if year != 'N/A' else 0
                except:
                    b, bd, p, yr = 0, 0, 999999, 0
                
                if bd >= 5 and b >= 2.5 and b <= 3.0 and p <= 600000 and yr >= 2017:
                    all_listings.append({
                        'address': addr,
                        'price': price,
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year_built': year,
                        'url': detail,
                        'area': area_name
                    })
                    print(f'  MATCH: {addr} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | {year}')
        else:
            # Try alternative pattern
            match2 = re.search(r'"searchResults":\{"listResults":(\[.*?\]),"mapResults"', resp.text)
            if match2:
                print(f'  Found alternative pattern')
            else:
                print(f'  No embedded data found')
                # Check if blocked
                if 'captcha' in resp.text.lower() or 'blocked' in resp.text.lower():
                    print(f'  BLOCKED by Zillow')
    except Exception as e:
        print(f'  Error: {e}')

print(f'\n=== TOTAL MATCHING LISTINGS: {len(all_listings)} ===')
for i, l in enumerate(all_listings):
    print(f"{i+1}. {l['address']} | {l['price']} | {l['beds']}bd/{l['baths']}ba | {l['sqft']}sqft | Built {l['year_built']} | {l['url']}")

# Save results
with open('zillow_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)
print(f'Results saved to zillow_results.json')
