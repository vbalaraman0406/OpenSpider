import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

results = []

# Let me first inspect the actual JSON structure from one response
cities_redfin = {
    'Vancouver, WA': '19118',
    'Ridgefield, WA': '17460', 
    'Battle Ground, WA': '2590',
    'Camas, WA': '4830',
    'Washougal, WA': '23370',
}

for city, region_id in cities_redfin.items():
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type=6&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        
        resp = requests.get(url, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            text = resp.text
            if text.startswith('{}&&'):
                text = text[4:]
            data = json.loads(text)
            homes = data.get('payload', {}).get('homes', [])
            print(f"\n{city}: {len(homes)} total homes returned")
            
            # Print first home's full structure to understand the data
            if homes and city == 'Vancouver, WA':
                h = homes[0]
                print(f"  Sample home keys: {list(h.keys())}")
                # Print key fields
                for key in ['price', 'beds', 'baths', 'sqFt', 'yearBuilt', 'streetAddress', 'url', 'listingType', 'propertyType']:
                    val = h.get(key, 'MISSING')
                    print(f"    {key}: {val} (type: {type(val).__name__})")
                # Check for nested price
                if isinstance(h.get('price'), dict):
                    print(f"    price.value: {h['price'].get('value')}")
            
            # Now filter and extract
            for h in homes:
                # Extract price
                price_raw = h.get('price', {})
                if isinstance(price_raw, dict):
                    price = price_raw.get('value', 0)
                else:
                    price = price_raw or 0
                
                beds = h.get('beds', 0)
                baths = h.get('baths', 0)
                
                sqft_raw = h.get('sqFt', {})
                if isinstance(sqft_raw, dict):
                    sqft = sqft_raw.get('value', 0)
                else:
                    sqft = sqft_raw or 0
                
                yr_raw = h.get('yearBuilt', {})
                if isinstance(yr_raw, dict):
                    yr = yr_raw.get('value', 0)
                else:
                    yr = yr_raw or 0
                
                # Extract address
                addr_raw = h.get('streetAddress', {})
                if isinstance(addr_raw, dict):
                    addr = addr_raw.get('assembledAddress', str(addr_raw))
                else:
                    addr = str(addr_raw) if addr_raw else 'N/A'
                
                link = h.get('url', '')
                if link and not link.startswith('http'):
                    link = 'https://www.redfin.com' + link
                
                # Apply our filters: 5+ beds, 2.5-3 baths, <=600000, built >= 2017
                try:
                    price_num = float(price) if price else 0
                    beds_num = int(beds) if beds else 0
                    baths_num = float(baths) if baths else 0
                    yr_num = int(yr) if yr else 0
                except:
                    continue
                
                if beds_num >= 5 and 2.5 <= baths_num <= 3.0 and price_num <= 600000 and yr_num >= 2017:
                    results.append({
                        'address': addr,
                        'price': f"${int(price_num):,}",
                        'beds': beds_num,
                        'baths': baths_num,
                        'sqft': sqft,
                        'year': yr_num,
                        'url': link,
                        'source': 'Redfin',
                        'city': city
                    })
                    print(f"  MATCH: {addr} | ${int(price_num):,} | {beds_num}bd/{baths_num}ba | {sqft}sqft | Built:{yr_num}")
    except Exception as e:
        print(f"  Error for {city}: {e}")

# Also search broader area with lat/lng for Brush Prairie
print("\n--- Brush Prairie (polygon search) ---")
try:
    # Brush Prairie approximate bounds
    url = 'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&num_homes=350&ord=redfin-recommended-asc&page_number=1&poly=-122.78%2045.72%2C-122.65%2045.72%2C-122.65%2045.78%2C-122.78%2045.78&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        text = resp.text
        if text.startswith('{}&&'):
            text = text[4:]
        data = json.loads(text)
        homes = data.get('payload', {}).get('homes', [])
        print(f"  {len(homes)} homes in Brush Prairie area")
        for h in homes:
            price_raw = h.get('price', {})
            price = price_raw.get('value', 0) if isinstance(price_raw, dict) else (price_raw or 0)
            beds = h.get('beds', 0) or 0
            baths = h.get('baths', 0) or 0
            sqft_raw = h.get('sqFt', {})
            sqft = sqft_raw.get('value', 0) if isinstance(sqft_raw, dict) else (sqft_raw or 0)
            yr_raw = h.get('yearBuilt', {})
            yr = yr_raw.get('value', 0) if isinstance(yr_raw, dict) else (yr_raw or 0)
            addr_raw = h.get('streetAddress', {})
            addr = addr_raw.get('assembledAddress', str(addr_raw)) if isinstance(addr_raw, dict) else str(addr_raw)
            link = h.get('url', '')
            if link and not link.startswith('http'):
                link = 'https://www.redfin.com' + link
            try:
                price_num = float(price)
                beds_num = int(beds)
                baths_num = float(baths)
                yr_num = int(yr)
            except:
                continue
            if beds_num >= 5 and 2.5 <= baths_num <= 3.0 and price_num <= 600000 and yr_num >= 2017:
                # Check not duplicate
                if not any(r['url'] == link for r in results):
                    results.append({
                        'address': addr, 'price': f"${int(price_num):,}", 'beds': beds_num,
                        'baths': baths_num, 'sqft': sqft, 'year': yr_num, 'url': link,
                        'source': 'Redfin', 'city': 'Brush Prairie, WA'
                    })
                    print(f"  MATCH: {addr} | ${int(price_num):,} | {beds_num}bd/{baths_num}ba | {sqft}sqft | Built:{yr_num}")
except Exception as e:
    print(f"  Error: {e}")

print(f"\n\n=== TOTAL MATCHING RESULTS: {len(results)} ===")
for r in results:
    print(f"{r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built:{r['year']} | {r['source']} | {r['url']}")

with open('redfin_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"Saved to redfin_results.json")
