import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

results = []

# Step 1: Get correct region IDs from Redfin autocomplete
cities = ['Vancouver WA', 'Ridgefield WA', 'Battle Ground WA', 'Camas WA', 'Washougal WA']
region_map = {}

for city in cities:
    try:
        url = f'https://www.redfin.com/stingray/do/location-autocomplete?location={city.replace(" ", "%20")}&start=0&count=5&v=2'
        resp = requests.get(url, headers=headers, timeout=10)
        text = resp.text
        if text.startswith('{}&&'):
            text = text[4:]
        data = json.loads(text)
        if 'payload' in data and 'sections' in data['payload']:
            for section in data['payload']['sections']:
                for row in section.get('rows', []):
                    if 'id' in row:
                        region_map[city] = {
                            'id': row['id'],
                            'type': row.get('type', ''),
                            'subType': row.get('subType', ''),
                            'url': row.get('url', ''),
                            'name': row.get('name', '')
                        }
                        print(f"{city}: id={row['id']}, type={row.get('type')}, name={row.get('name')}, url={row.get('url')}")
                        break
                if city in region_map:
                    break
    except Exception as e:
        print(f"Error for {city}: {e}")

print(f"\nFound {len(region_map)} regions")

# Step 2: Search each region with correct IDs
for city, info in region_map.items():
    try:
        region_id = info['id']
        region_type = info.get('type', '6')
        # Map Redfin type codes: 2=city, 6=zip, etc.
        # type 2 = city, type 6 = neighborhood
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type={region_type}&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            text = resp.text
            if text.startswith('{}&&'):
                text = text[4:]
            data = json.loads(text)
            homes = data.get('payload', {}).get('homes', [])
            print(f"\n{city}: {len(homes)} homes returned")
            
            # Check first home's location
            if homes:
                h = homes[0]
                print(f"  First home: {h.get('streetLine','')} {h.get('city','')} {h.get('state','')}")
            
            for h in homes:
                beds = h.get('beds', 0) or 0
                if int(beds) < 5:
                    continue
                
                baths = float(h.get('baths', 0) or 0)
                price_raw = h.get('price', {})
                price = price_raw.get('value', 0) if isinstance(price_raw, dict) else (int(price_raw) if price_raw else 0)
                yr_raw = h.get('yearBuilt', {})
                yr = yr_raw.get('value', 0) if isinstance(yr_raw, dict) else (int(yr_raw) if yr_raw else 0)
                sqft_raw = h.get('sqFt', {})
                sqft = sqft_raw.get('value', 0) if isinstance(sqft_raw, dict) else (int(sqft_raw) if sqft_raw else 0)
                
                addr = f"{h.get('streetLine', '')} {h.get('city', '')} {h.get('state', '')} {h.get('zip', '')}".strip()
                link = h.get('url', '')
                if link and not link.startswith('http'):
                    link = 'https://www.redfin.com' + link
                
                state = h.get('state', '')
                if state != 'WA':
                    continue
                
                if 2.5 <= baths <= 3.0 and price <= 600000 and yr >= 2017:
                    results.append({
                        'address': addr,
                        'price': f"${price:,}",
                        'beds': int(beds),
                        'baths': baths,
                        'sqft': sqft,
                        'year': yr,
                        'url': link,
                        'source': 'Redfin'
                    })
                    print(f"  MATCH: {addr} | ${price:,} | {int(beds)}bd/{baths}ba | {sqft}sqft | Built:{yr}")
                else:
                    if int(beds) >= 5:
                        reasons = []
                        if baths < 2.5 or baths > 3.0: reasons.append(f'baths={baths}')
                        if price > 600000: reasons.append(f'price=${price:,}')
                        if yr < 2017: reasons.append(f'year={yr}')
                        if reasons:
                            pass  # Don't print filtered out to save output
    except Exception as e:
        print(f"Error for {city}: {e}")

print(f"\n=== TOTAL MATCHING: {len(results)} ===")
for r in results:
    print(f"{r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built:{r['year']} | {r['url']}")

with open('redfin_results.json', 'w') as f:
    json.dump(results, f, indent=2)
