import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.redfin.com/',
}

# Vancouver WA bounding box covering Vancouver, Ridgefield, Battle Ground, Camas, Washougal, Brush Prairie
# Approx coords: lat 45.55-45.85, lon -122.80 to -122.30
poly = '-122.80 45.55 -122.30 45.55 -122.30 45.85 -122.80 45.85'
poly_encoded = poly.replace(' ', '%20')

url = f'https://www.redfin.com/stingray/api/gis?al=1&include_nearby_homes=true&market=portland&max_price=600000&min_baths=2.5&max_baths=3&min_beds=5&min_year_built=2017&num_homes=350&ord=redfin-recommended-asc&page_number=1&poly={poly_encoded}&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'

try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f'Status: {resp.status_code}')
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    data = json.loads(text)
    homes = data.get('payload', {}).get('homes', [])
    print(f'Found {len(homes)} homes')
    for h in homes:
        price = h.get('price', {}).get('value', 'N/A') if isinstance(h.get('price'), dict) else h.get('price', 'N/A')
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
    import traceback
    traceback.print_exc()
    # Print raw response for debugging
    try:
        print(f'Response text (first 1000): {resp.text[:1000]}')
    except:
        pass
