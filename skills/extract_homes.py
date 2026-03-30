import requests
import json

url = 'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&min_stories=1&num_homes=20&ord=price-asc&page_number=1&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8&min_num_beds=5&min_num_baths=2.5&min_year_built=2020'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.redfin.com/city/18791/WA/Vancouver'
}

import warnings
warnings.filterwarnings('ignore')

r = requests.get(url, headers=headers, timeout=15, verify=False)
data = r.text
if data.startswith('{}&&'):
    data = data[4:]
parsed = json.loads(data)
homes = parsed.get('payload', {}).get('homes', [])

print(f'Total homes found: {len(homes)}\n')

results = []
for i, h in enumerate(homes):
    price = h.get('price', {}).get('value', 'N/A') if isinstance(h.get('price'), dict) else h.get('price', 'N/A')
    street = h.get('streetLine', 'N/A')
    city = h.get('city', '')
    state = h.get('state', '')
    zipcode = h.get('zip', h.get('postalCode', ''))
    beds = h.get('beds', 'N/A')
    baths = h.get('baths', 'N/A')
    sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
    yr = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
    lot = h.get('lotSize', {}).get('value', 'N/A') if isinstance(h.get('lotSize'), dict) else h.get('lotSize', 'N/A')
    url_path = h.get('url', '')
    full_url = f'https://www.redfin.com{url_path}' if url_path else 'N/A'
    tags = h.get('listingTags', [])
    key_facts = h.get('keyFacts', [])
    is_new = h.get('isNewConstruction', False)
    community = h.get('newConstructionCommunityInfo', {})
    comm_name = ''
    if isinstance(community, dict):
        comm_name = community.get('communityName', '')
    
    # Format price
    if isinstance(price, (int, float)):
        price_str = f'${price:,.0f}'
    else:
        price_str = str(price)
    
    # Format lot size
    if isinstance(lot, (int, float)):
        lot_str = f'{lot:,.0f} sqft'
    else:
        lot_str = str(lot)
    
    notable = []
    if is_new:
        notable.append('New Construction')
    if comm_name:
        notable.append(f'Community: {comm_name}')
    if tags:
        notable.extend(tags[:3])
    
    print(f'{i+1}. {price_str} | {street}, {city}, {state} {zipcode}')
    print(f'   {beds}bd/{baths}ba | {sqft} sqft | Built: {yr} | Lot: {lot_str}')
    print(f'   URL: {full_url}')
    print(f'   Notable: {", ".join(notable)}')
    print()
    
    results.append({
        'rank': i+1,
        'price': price_str,
        'address': f'{street}, {city}, {state} {zipcode}',
        'beds': beds,
        'baths': baths,
        'sqft': sqft,
        'year_built': yr,
        'lot': lot_str,
        'url': full_url,
        'notable': ', '.join(notable)
    })

# Save to JSON for later use
with open('homes_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nSaved {len(results)} homes to homes_data.json')
