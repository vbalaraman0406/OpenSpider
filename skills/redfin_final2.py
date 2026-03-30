import requests
import json
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Upgrade-Insecure-Requests': '1',
})
session.get('https://www.redfin.com/', timeout=15, verify=False)
session.headers.update({
    'Accept': '*/*',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://www.redfin.com/',
})

# Target cities in Clark County WA
target_cities = {'vancouver', 'ridgefield', 'battle ground', 'camas', 'washougal', 'brush prairie'}

all_listings = []
seen_urls = set()

# Search multiple region IDs and bounding boxes
search_urls = [
    # Bounding box covering Clark County WA
    ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
     '&num_homes=350&ord=redfin-recommended-asc&page_number=1'
     '&poly=-122.85%2045.55%2C-122.15%2045.55%2C-122.15%2045.85%2C-122.85%2045.85'
     '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
     '&min_num_beds=5&max_price=600000&min_year_built=2017'),
    # Region 30772
    ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
     '&num_homes=350&ord=redfin-recommended-asc&page_number=1'
     '&region_id=30772&region_type=6'
     '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
     '&min_num_beds=5&max_price=600000&min_year_built=2017'),
]

for gis_url in search_urls:
    try:
        resp = session.get(gis_url, timeout=20, verify=False)
        data = resp.text
        if data.startswith('{}&&'):
            data = data[4:]
        parsed = json.loads(data)
        homes = parsed.get('payload', {}).get('homes', [])
        print(f'Search returned {len(homes)} raw homes')
        
        for home in homes:
            # Extract fields with proper structure handling
            price_obj = home.get('price', {})
            price = price_obj.get('value', 0) if isinstance(price_obj, dict) else (price_obj if price_obj else 0)
            
            beds = home.get('beds', 0)
            baths = home.get('baths', 0)
            
            sqft_obj = home.get('sqFt', {})
            sqft = sqft_obj.get('value', 'N/A') if isinstance(sqft_obj, dict) else (sqft_obj if sqft_obj else 'N/A')
            
            yb_obj = home.get('yearBuilt', {})
            yb = yb_obj.get('value', 0) if isinstance(yb_obj, dict) else (yb_obj if yb_obj else 0)
            
            sl_obj = home.get('streetLine', {})
            addr = sl_obj.get('value', '') if isinstance(sl_obj, dict) else (sl_obj if sl_obj else '')
            
            city = home.get('city', '')
            state = home.get('state', '')
            zipcode = home.get('zip', '')
            url_path = home.get('url', '')
            
            listing_url = f"https://www.redfin.com{url_path}" if url_path else 'N/A'
            
            # Skip duplicates
            if listing_url in seen_urls:
                continue
            
            # CLIENT-SIDE FILTERS
            # Must be in WA
            if state != 'WA':
                continue
            # Must be in target cities
            if city.lower() not in target_cities:
                continue
            # 5+ beds
            if beds < 5:
                continue
            # 2.5-3 baths
            try:
                b = float(baths)
                if b < 2.5 or b > 3.0:
                    continue
            except:
                continue
            # Under $600K
            if price > 600000:
                continue
            # Built 2017+
            if yb < 2017:
                continue
            
            seen_urls.add(listing_url)
            full_addr = f"{addr}, {city}, {state} {zipcode}"
            all_listings.append({
                'address': full_addr,
                'price': price,
                'beds': beds,
                'baths': baths,
                'sqft': sqft,
                'year_built': yb,
                'url': listing_url
            })
    except Exception as e:
        print(f'Search error: {e}')

print(f'\nTotal matching listings: {len(all_listings)}')

# Save to file
with open('redfin_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)

# Print markdown table
if all_listings:
    print('\n| Address | Price | Beds | Baths | SqFt | Year Built | URL |')
    print('|---------|-------|------|-------|------|------------|-----|')
    for l in all_listings:
        price_str = f"${l['price']:,.0f}" if isinstance(l['price'], (int, float)) else str(l['price'])
        print(f"| {l['address']} | {price_str} | {l['beds']} | {l['baths']} | {l['sqft']} | {l['year_built']} | [Link]({l['url']}) |")
else:
    print('\nNo matching listings found with all filters applied.')
    # Debug: show what we filtered out
    print('\nDebug - checking what cities/states/beds/baths are in the data...')
    for gis_url in search_urls[:1]:
        resp = session.get(gis_url, timeout=20, verify=False)
        data = resp.text
        if data.startswith('{}&&'):
            data = data[4:]
        parsed = json.loads(data)
        homes = parsed.get('payload', {}).get('homes', [])
        wa_homes = [h for h in homes if h.get('state') == 'WA']
        print(f'WA homes: {len(wa_homes)} out of {len(homes)}')
        cities_in_wa = set(h.get('city', '') for h in wa_homes)
        print(f'WA cities: {cities_in_wa}')
        beds_in_wa = set(h.get('beds', 0) for h in wa_homes)
        print(f'WA beds values: {sorted(beds_in_wa)}')
        # Show homes with 5+ beds in target cities
        for h in wa_homes:
            if h.get('beds', 0) >= 5 and h.get('city', '').lower() in target_cities:
                p = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else h.get('price', 0)
                b = h.get('baths', 0)
                y = h.get('yearBuilt', {}).get('value', 0) if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 0)
                print(f"  5+bed: city={h.get('city')}, beds={h.get('beds')}, baths={b}, price={p}, year={y}")
