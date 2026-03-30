import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.redfin.com/',
}

# Try Redfin's stingray API endpoint for search
url = 'https://www.redfin.com/stingray/api/gis?al=1&include_nearby_homes=true&market=portland&min_stories=1&num_homes=350&ord=redfin-recommended-asc&page_number=1&poly=-122.91382%2045.56498%20-122.38098%2045.56498%20-122.38098%2045.78542%20-122.91382%2045.78542&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'

# Also try with filters
url2 = 'https://www.redfin.com/stingray/api/gis?al=1&include_nearby_homes=true&market=portland&max_price=600000&min_baths=2.5&max_baths=3&min_beds=5&min_year_built=2017&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id=18791&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'

try:
    resp = requests.get(url2, headers=headers, timeout=15)
    print(f'Status: {resp.status_code}')
    # Redfin prepends {}&&& to JSON responses
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    data = json.loads(text)
    homes = data.get('payload', {}).get('homes', [])
    print(f'Found {len(homes)} homes')
    for h in homes[:20]:
        price = h.get('price', {}).get('value', 'N/A')
        addr = h.get('streetLine', {}).get('value', '') if isinstance(h.get('streetLine'), dict) else h.get('streetLine', '')
        city = h.get('city', '')
        state = h.get('state', '')
        zipcode = h.get('zip', '')
        beds = h.get('beds', 'N/A')
        baths = h.get('baths', 'N/A')
        sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
        yr = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
        url_path = h.get('url', '')
        link = f'https://www.redfin.com{url_path}' if url_path else 'N/A'
        print(f'${price} | {addr}, {city}, {state} {zipcode} | {beds}bd/{baths}ba | {sqft} sqft | Built: {yr} | {link}')
except Exception as e:
    print(f'Error: {e}')
    # Try alternate approach
    print('Trying HTML scrape...')
    try:
        html_url = 'https://www.redfin.com/city/18791/WA/Vancouver/filter/property-type=house,min-beds=5,min-baths=2.5,max-baths=3,max-price=600000,min-year-built=2017'
        resp2 = requests.get(html_url, headers=headers, timeout=15)
        print(f'HTML Status: {resp2.status_code}')
        print(resp2.text[:2000])
    except Exception as e2:
        print(f'HTML Error: {e2}')
