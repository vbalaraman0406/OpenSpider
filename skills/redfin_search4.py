import requests
import json
import csv
import io
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# Let's try to get the Redfin page HTML to find region IDs
# First try the search page URL
try:
    url = 'https://www.redfin.com/city/18959/WA/Vancouver'
    resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
    print(f"Vancouver page: Status {resp.status_code}, URL: {resp.url}")
    # Look for region_id in the page
    match = re.search(r'region_id["\s:=]+(\d+)', resp.text)
    if match:
        print(f"Found region_id: {match.group(1)}")
    match2 = re.search(r'regionId["\s:=]+(\d+)', resp.text)
    if match2:
        print(f"Found regionId: {match2.group(1)}")
    # Check if redirected
    print(f"Final URL: {resp.url}")
    print(f"Page title: {re.search(r'<title>(.*?)</title>', resp.text[:5000]).group(1) if re.search(r'<title>(.*?)</title>', resp.text[:5000]) else 'N/A'}")
except Exception as e:
    print(f"Error: {e}")

# Try Redfin's location search API with different format
print("\n=== Trying location search ===")
try:
    url = 'https://www.redfin.com/stingray/do/location-autocomplete?location=Vancouver,%20WA&start=0&count=10&v=2&al=1&iss=false&ooa=true&mrs=false'
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    print(f"Response (first 1000): {text[:1000]}")
    if resp.status_code == 200 and len(text) > 10:
        try:
            data = json.loads(text)
            print(f"Parsed JSON keys: {list(data.keys())}")
            payload = data.get('payload', {})
            print(f"Payload keys: {list(payload.keys()) if isinstance(payload, dict) else 'not dict'}")
            if isinstance(payload, dict):
                sections = payload.get('sections', [])
                for s in sections:
                    for row in s.get('rows', []):
                        print(f"  {row}")
        except:
            pass
except Exception as e:
    print(f"Error: {e}")

# Try with a broader approach - use Redfin's map-based search
print("\n=== Trying map-based search ===")
# Vancouver WA approximate bounds
# lat: 45.58-45.72, lng: -122.75 to -122.55
try:
    url = 'https://www.redfin.com/stingray/api/gis?al=1&min_beds=5&max_price=600000&min_year_built=2017&status=9&uipt=1&v=8&poly=-122.80%2045.55%2C-122.25%2045.55%2C-122.25%2045.85%2C-122.80%2045.85%2C-122.80%2045.55&num_homes=100'
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Map search status: {resp.status_code}")
    text = resp.text
    if text.startswith('{}&&'):
        text = text[4:]
    if resp.status_code == 200 and len(text) > 10:
        try:
            data = json.loads(text)
            homes = data.get('payload', {}).get('homes', [])
            print(f"Found {len(homes)} homes in map search")
            for h in homes[:20]:
                price = h.get('price', {}).get('value', 'N/A') if isinstance(h.get('price'), dict) else h.get('price', 'N/A')
                beds = h.get('beds', 'N/A')
                baths = h.get('baths', 'N/A')
                sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
                year = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
                street = h.get('streetLine', {}).get('value', '') if isinstance(h.get('streetLine'), dict) else h.get('streetLine', '')
                city = h.get('city', '')
                state = h.get('state', '')
                zipcode = h.get('zip', '')
                url_path = h.get('url', '')
                print(f"  ${price} | {beds}bd/{baths}ba | {sqft}sqft | Built {year} | {street}, {city}, {state} {zipcode} | https://www.redfin.com{url_path}")
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
            print(f"Response: {text[:500]}")
    else:
        print(f"Response: {text[:300]}")
except Exception as e:
    print(f"Error: {e}")

# Also try CSV with polygon
print("\n=== Trying CSV with polygon ===")
try:
    url = 'https://www.redfin.com/stingray/api/gis-csv?al=1&min_beds=5&max_price=600000&min_year_built=2017&status=9&uipt=1&v=8&poly=-122.80%2045.55%2C-122.25%2045.55%2C-122.25%2045.85%2C-122.80%2045.85%2C-122.80%2045.55&num_homes=100'
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"CSV polygon search status: {resp.status_code}")
    if resp.status_code == 200:
        text = resp.text
        if 'ADDRESS' in text:
            reader = csv.DictReader(io.StringIO(text))
            count = 0
            results = []
            for row in reader:
                addr = row.get('ADDRESS', '')
                city_val = row.get('CITY', '')
                state = row.get('STATE OR PROVINCE', '')
                zipcode = row.get('ZIP OR POSTAL CODE', '')
                price = row.get('PRICE', '')
                beds = row.get('BEDS', '')
                baths = row.get('BATHS', '')
                sqft = row.get('SQUARE FEET', '')
                year = row.get('YEAR BUILT', '')
                url_val = row.get('URL (SEE https://www.redfin.com/buy-a-home/comparative-market-analysis FOR INFO ON PRICING)', '')
                status = row.get('STATUS', '')
                
                if not addr or state != 'WA':
                    continue
                
                full_addr = f"{addr}, {city_val}, {state} {zipcode}"
                full_url = f"https://www.redfin.com{url_val}" if url_val and not url_val.startswith('http') else (url_val or 'N/A')
                print(f"  ${price} | {beds}bd/{baths}ba | {sqft}sqft | Built {year} | {full_addr} | {status}")
                results.append({
                    'address': full_addr,
                    'price': price,
                    'beds': beds,
                    'baths': baths,
                    'sqft': sqft,
                    'year': year,
                    'url': full_url,
                    'status': status,
                    'source': 'Redfin'
                })
                count += 1
            print(f"  Total WA results: {count}")
            
            # Save results
            with open('redfin_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Saved {len(results)} results to redfin_results.json")
        else:
            print(f"Non-CSV response: {text[:300]}")
    else:
        print(f"Error: {resp.text[:300]}")
except Exception as e:
    print(f"Error: {e}")
