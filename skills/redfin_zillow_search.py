import requests
import re
import json
from urllib.parse import quote

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
}

results = []

# ===== REDFIN APPROACH =====
print('=== Redfin Search ===')
try:
    # Redfin stingray API for search
    # First get region ID for Vancouver WA
    redfin_search_url = 'https://www.redfin.com/stingray/do/location-autocomplete'
    resp = requests.get(redfin_search_url, params={'location': 'Vancouver, WA', 'v': '2'}, headers=headers, timeout=15)
    print(f'Redfin autocomplete status: {resp.status_code}')
    # Parse the response (it's JSONP-like)
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    data = json.loads(text)
    print(f'Redfin autocomplete data keys: {list(data.keys()) if isinstance(data, dict) else "not dict"}')
    
    # Try to find region info
    if 'payload' in data:
        sections = data['payload'].get('sections', [])
        for section in sections:
            for row in section.get('rows', []):
                name = row.get('name', '')
                if 'Vancouver' in name and 'WA' in name:
                    region_id = row.get('id', '')
                    region_type = row.get('type', '')
                    print(f'Found: {name} - ID: {region_id}, Type: {region_type}')
                    break
except Exception as e:
    print(f'Redfin autocomplete error: {e}')

# Try Redfin gis-csv endpoint
print('\n=== Redfin CSV Download ===')
try:
    # Redfin allows CSV download of search results
    redfin_csv_url = 'https://www.redfin.com/stingray/api/gis-csv'
    params = {
        'al': '1',
        'market': 'portland',
        'min_stories': '1',
        'num_beds': '5',
        'num_baths': '2.5',
        'max_price': '600000',
        'min_year_built': '2017',
        'sf': '1,2,5,6,7',
        'status': '9',
        'uipt': '1',
        'v': '8',
        'region_id': '19418',
        'region_type': '6',
    }
    resp = requests.get(redfin_csv_url, params=params, headers=headers, timeout=15)
    print(f'Redfin CSV status: {resp.status_code}')
    if resp.status_code == 200:
        lines = resp.text.strip().split('\n')
        print(f'CSV lines: {len(lines)}')
        if len(lines) > 1:
            header = lines[0].split(',')
            print(f'Headers: {header[:15]}')
            for line in lines[1:21]:  # First 20 results
                cols = line.split(',')
                # Find relevant column indices
                try:
                    addr_idx = next(i for i, h in enumerate(header) if 'ADDRESS' in h.upper())
                    price_idx = next(i for i, h in enumerate(header) if 'PRICE' in h.upper() and 'LIST' not in h.upper())
                    beds_idx = next(i for i, h in enumerate(header) if 'BED' in h.upper())
                    baths_idx = next(i for i, h in enumerate(header) if 'BATH' in h.upper())
                    sqft_idx = next(i for i, h in enumerate(header) if 'SQUARE' in h.upper() or 'SQFT' in h.upper())
                    year_idx = next(i for i, h in enumerate(header) if 'YEAR' in h.upper())
                    url_idx = next(i for i, h in enumerate(header) if 'URL' in h.upper())
                    city_idx = next(i for i, h in enumerate(header) if 'CITY' in h.upper())
                    state_idx = next(i for i, h in enumerate(header) if 'STATE' in h.upper())
                    zip_idx = next(i for i, h in enumerate(header) if 'ZIP' in h.upper())
                except StopIteration:
                    print(f'Could not find all columns. Available: {header}')
                    break
                
                if len(cols) > max(addr_idx, price_idx, beds_idx, baths_idx):
                    addr = cols[addr_idx].strip('"')
                    city = cols[city_idx].strip('"') if city_idx < len(cols) else ''
                    state = cols[state_idx].strip('"') if state_idx < len(cols) else ''
                    zipcode = cols[zip_idx].strip('"') if zip_idx < len(cols) else ''
                    full_addr = f"{addr}, {city}, {state} {zipcode}"
                    price = cols[price_idx].strip('"')
                    beds = cols[beds_idx].strip('"')
                    baths = cols[baths_idx].strip('"')
                    sqft = cols[sqft_idx].strip('"') if sqft_idx < len(cols) else 'N/A'
                    year = cols[year_idx].strip('"') if year_idx < len(cols) else 'N/A'
                    url = cols[url_idx].strip('"') if url_idx < len(cols) else 'N/A'
                    if not url.startswith('http'):
                        url = 'https://www.redfin.com' + url
                    
                    # Filter: baths <= 3
                    try:
                        baths_num = float(baths)
                        if baths_num > 3:
                            continue
                    except:
                        pass
                    
                    results.append({
                        'address': full_addr,
                        'price': price,
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year_built': year,
                        'source': 'Redfin',
                        'url': url
                    })
        else:
            print(f'Response text: {resp.text[:500]}')
    else:
        print(f'Response: {resp.text[:500]}')
except Exception as e:
    print(f'Redfin CSV error: {e}')

# ===== ZILLOW HTML SCRAPE =====
print('\n=== Zillow HTML Scrape ===')
try:
    zillow_url = 'https://www.zillow.com/vancouver-wa/houses/5-_beds/2.5-_baths/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A600000%7D%2C%22beds%22%3A%7B%22min%22%3A5%7D%2C%22baths%22%3A%7B%22min%22%3A2.5%7D%2C%22built%22%3A%7B%22min%22%3A%222017%22%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    zillow_headers = headers.copy()
    zillow_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    resp = requests.get(zillow_url, headers=zillow_headers, timeout=15, allow_redirects=True)
    print(f'Zillow HTML status: {resp.status_code}, URL: {resp.url}')
    
    # Look for preloaded search data in the HTML
    # Zillow embeds search results as JSON in a script tag
    match = re.search(r'"listResults"\s*:\s*\[(.+?)\]\s*,\s*"mapResults"', resp.text, re.DOTALL)
    if match:
        print('Found listResults in HTML!')
        # Parse individual results
        list_text = '[' + match.group(1) + ']'
        try:
            list_data = json.loads(list_text)
            print(f'Parsed {len(list_data)} list results')
        except:
            print('Could not parse listResults JSON')
    else:
        # Try another pattern
        match2 = re.search(r'"searchResults"\s*:\s*\{(.+?)\}\s*\}', resp.text[:50000], re.DOTALL)
        if match2:
            print('Found searchResults pattern')
        else:
            print(f'No search results found in HTML. Page length: {len(resp.text)}')
            # Check if we got redirected
            if 'captcha' in resp.text.lower() or 'robot' in resp.text.lower():
                print('CAPTCHA detected!')
            # Print a snippet
            print(f'HTML snippet: {resp.text[:300]}')
except Exception as e:
    print(f'Zillow HTML error: {e}')

print(f'\n=== TOTAL RESULTS: {len(results)} ===')
for r in results:
    print(f"  {r['address']} | ${r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built {r['year_built']} | {r['source']} | {r['url']}")

with open('search_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f'Results saved to search_results.json')
