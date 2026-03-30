import requests
import json
import warnings
warnings.filterwarnings('ignore')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Sec-Ch-Ua': '"Google Chrome";v="131"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
})

# Get cookies from homepage
session.get('https://www.redfin.com/', timeout=15, verify=False)

# Update headers for API calls
session.headers.update({
    'Accept': '*/*',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Referer': 'https://www.redfin.com/',
})

# Region IDs to try for WA cities
# 30772 worked for some area. Let me also try bounding box approach
# covering all of Clark County WA (Vancouver, Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie)
# Bounding box: lat 45.55-45.85, lng -122.8 to -122.2

all_listings = []

# Try bounding box search covering entire Clark County WA area
gis_url = ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
           '&num_homes=350&ord=redfin-recommended-asc&page_number=1'
           '&poly=-122.8%2045.55%2C-122.2%2045.55%2C-122.2%2045.85%2C-122.8%2045.85'
           '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
           '&min_num_beds=5&max_price=600000&min_year_built=2017')

try:
    resp = session.get(gis_url, timeout=20, verify=False)
    data = resp.text
    if data.startswith('{}&&'):
        data = data[4:]
    parsed = json.loads(data)
    homes = parsed.get('payload', {}).get('homes', [])
    print(f'Bounding box search: Found {len(homes)} raw homes')
    
    for home in homes:
        price = home.get('price', {}).get('value', 'N/A') if isinstance(home.get('price'), dict) else home.get('price', 'N/A')
        beds = home.get('beds', 'N/A')
        baths = home.get('baths', 'N/A')
        sqft = home.get('sqFt', {}).get('value', 'N/A') if isinstance(home.get('sqFt'), dict) else home.get('sqFt', 'N/A')
        yb = home.get('yearBuilt', {}).get('value', 'N/A') if isinstance(home.get('yearBuilt'), dict) else home.get('yearBuilt', 'N/A')
        addr = home.get('streetLine', {}).get('value', '') if isinstance(home.get('streetLine'), dict) else home.get('streetLine', '')
        city = home.get('city', '')
        state = home.get('state', '')
        zipcode = home.get('zip', '')
        url_path = home.get('url', '')
        
        full_addr = f"{addr}, {city}, {state} {zipcode}"
        listing_url = f"https://www.redfin.com{url_path}" if url_path else 'N/A'
        
        # Filter baths 2.5-3
        try:
            baths_num = float(baths) if baths != 'N/A' else 0
            if baths_num < 2.5 or baths_num > 3:
                continue
        except:
            continue
        
        # Filter: must be in WA
        if state != 'WA':
            continue
        
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
    print(f'Bounding box error: {e}')

# Also try region_id=30772 which returned results before
try:
    gis_url2 = ('https://www.redfin.com/stingray/api/gis?al=1&market=seattle'
                '&num_homes=350&ord=redfin-recommended-asc&page_number=1'
                '&region_id=30772&region_type=6'
                '&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
                '&min_num_beds=5&max_price=600000&min_year_built=2017')
    resp = session.get(gis_url2, timeout=20, verify=False)
    data = resp.text
    if data.startswith('{}&&'):
        data = data[4:]
    parsed = json.loads(data)
    homes = parsed.get('payload', {}).get('homes', [])
    print(f'Region 30772 search: Found {len(homes)} raw homes')
    
    existing_urls = {l['url'] for l in all_listings}
    
    for home in homes:
        price = home.get('price', {}).get('value', 'N/A') if isinstance(home.get('price'), dict) else home.get('price', 'N/A')
        beds = home.get('beds', 'N/A')
        baths = home.get('baths', 'N/A')
        sqft = home.get('sqFt', {}).get('value', 'N/A') if isinstance(home.get('sqFt'), dict) else home.get('sqFt', 'N/A')
        yb = home.get('yearBuilt', {}).get('value', 'N/A') if isinstance(home.get('yearBuilt'), dict) else home.get('yearBuilt', 'N/A')
        addr = home.get('streetLine', {}).get('value', '') if isinstance(home.get('streetLine'), dict) else home.get('streetLine', '')
        city = home.get('city', '')
        state = home.get('state', '')
        zipcode = home.get('zip', '')
        url_path = home.get('url', '')
        
        full_addr = f"{addr}, {city}, {state} {zipcode}"
        listing_url = f"https://www.redfin.com{url_path}" if url_path else 'N/A'
        
        if listing_url in existing_urls:
            continue
        
        try:
            baths_num = float(baths) if baths != 'N/A' else 0
            if baths_num < 2.5 or baths_num > 3:
                continue
        except:
            continue
        
        if state != 'WA':
            continue
        
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
    print(f'Region 30772 error: {e}')

print(f'\nTotal matching listings after filtering: {len(all_listings)}')

# Save to file
with open('redfin_results.json', 'w') as f:
    json.dump(all_listings, f, indent=2)

# Print markdown table
for l in all_listings:
    price_str = f"${l['price']:,.0f}" if isinstance(l['price'], (int, float)) else str(l['price'])
    print(f"| {l['address']} | {price_str} | {l['beds']} | {l['baths']} | {l['sqft']} | {l['year_built']} | [Link]({l['url']}) |")
