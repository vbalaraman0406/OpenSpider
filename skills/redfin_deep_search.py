import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

results = []

# Redfin embeds data in window.__reactServerState or similar
# Let me try their stingray API which returns CSV data

cities_redfin = {
    'Vancouver, WA': '19118',
    'Ridgefield, WA': '17460', 
    'Battle Ground, WA': '2590',
    'Camas, WA': '4830',
    'Washougal, WA': '23370',
}

# Try Redfin's download endpoint (CSV)
for city, region_id in cities_redfin.items():
    try:
        # Redfin stingray API for search results
        url = f'https://www.redfin.com/stingray/api/gis?al=1&include_nearby_homes=true&market=seattle&min_stories=1&num_homes=50&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        url += '&min_num_beds=5&max_num_baths=3&min_num_baths=2.5&max_price=600000&min_year_built=2017'
        
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"\n{city} (stingray): Status {resp.status_code}")
        
        if resp.status_code == 200:
            text = resp.text
            if text.startswith('{}&&'):
                text = text[4:]
            try:
                data = json.loads(text)
                homes = data.get('payload', {}).get('homes', [])
                print(f"  Found {len(homes)} homes")
                for h in homes:
                    addr = h.get('streetAddress', {}).get('assembledAddress', 'N/A') if isinstance(h.get('streetAddress'), dict) else 'N/A'
                    price_info = h.get('price', {})
                    price = price_info.get('value', 'N/A') if isinstance(price_info, dict) else price_info
                    beds = h.get('beds', 'N/A')
                    baths = h.get('baths', 'N/A')
                    sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
                    yr = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
                    link = h.get('url', '')
                    if link and not link.startswith('http'):
                        link = 'https://www.redfin.com' + link
                    
                    results.append({
                        'address': addr,
                        'price': price,
                        'beds': beds,
                        'baths': baths,
                        'sqft': sqft,
                        'year': yr,
                        'url': link,
                        'source': 'Redfin',
                    })
                    print(f"  {addr} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | Built:{yr}")
            except json.JSONDecodeError:
                print(f"  JSON parse failed. First 500 chars: {text[:500]}")
        else:
            print(f"  Failed: {resp.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

# Also try Brush Prairie (unincorporated - use lat/lng bounds)
print("\n--- Brush Prairie (lat/lng search) ---")
try:
    url = 'https://www.redfin.com/stingray/api/gis?al=1&include_nearby_homes=true&market=seattle&min_stories=1&num_homes=50&ord=redfin-recommended-asc&page_number=1&poly=-122.7631%2045.7201%2C-122.6631%2045.7201%2C-122.6631%2045.7801%2C-122.7631%2045.7801&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
    url += '&min_num_beds=5&max_num_baths=3&min_num_baths=2.5&max_price=600000&min_year_built=2017'
    resp = requests.get(url, headers=headers, timeout=15)
    print(f"Brush Prairie: Status {resp.status_code}")
    if resp.status_code == 200:
        text = resp.text
        if text.startswith('{}&&'):
            text = text[4:]
        data = json.loads(text)
        homes = data.get('payload', {}).get('homes', [])
        print(f"  Found {len(homes)} homes")
        for h in homes:
            addr = h.get('streetAddress', {}).get('assembledAddress', 'N/A') if isinstance(h.get('streetAddress'), dict) else 'N/A'
            price_info = h.get('price', {})
            price = price_info.get('value', 'N/A') if isinstance(price_info, dict) else price_info
            beds = h.get('beds', 'N/A')
            baths = h.get('baths', 'N/A')
            sqft = h.get('sqFt', {}).get('value', 'N/A') if isinstance(h.get('sqFt'), dict) else h.get('sqFt', 'N/A')
            yr = h.get('yearBuilt', {}).get('value', 'N/A') if isinstance(h.get('yearBuilt'), dict) else h.get('yearBuilt', 'N/A')
            link = h.get('url', '')
            if link and not link.startswith('http'):
                link = 'https://www.redfin.com' + link
            results.append({
                'address': addr, 'price': price, 'beds': beds, 'baths': baths,
                'sqft': sqft, 'year': yr, 'url': link, 'source': 'Redfin',
            })
            print(f"  {addr} | ${price} | {beds}bd/{baths}ba | {sqft}sqft | Built:{yr}")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n\n=== TOTAL REDFIN RESULTS: {len(results)} ===")
for r in results:
    print(f"{r['address']} | ${r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built:{r['year']} | {r['url']}")

# Save results to JSON for later use
with open('redfin_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results to redfin_results.json")
