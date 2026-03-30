import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

results = []

# Correct Redfin city IDs (from autocomplete API)
# Vancouver WA = 18823
# Need to find others via autocomplete
cities_to_lookup = ['Ridgefield WA', 'Battle Ground WA', 'Camas WA', 'Washougal WA', 'Brush Prairie WA']
city_ids = {'Vancouver WA': ('18823', '2')}

for city in cities_to_lookup:
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
                    if 'id' in row and 'WA' in row.get('name', ''):
                        city_ids[city] = (str(row['id']), str(row.get('type', '2')))
                        print(f"{city}: id={row['id']}, type={row.get('type')}, name={row.get('name')}")
                        break
                if city in city_ids:
                    break
    except Exception as e:
        print(f"Autocomplete error for {city}: {e}")

print(f"\nCity IDs found: {json.dumps(city_ids, indent=2)}")

# Search each city via Redfin stingray API
for city, (region_id, region_type) in city_ids.items():
    try:
        url = f'https://www.redfin.com/stingray/api/gis?al=1&market=seattle&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type={region_type}&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            text = resp.text
            if text.startswith('{}&&'):
                text = text[4:]
            data = json.loads(text)
            homes = data.get('payload', {}).get('homes', [])
            
            # Verify location
            wa_homes = [h for h in homes if h.get('state') == 'WA']
            print(f"\n{city}: {len(homes)} total, {len(wa_homes)} in WA")
            
            for h in wa_homes:
                beds = int(h.get('beds', 0) or 0)
                if beds < 5:
                    continue
                baths = float(h.get('baths', 0) or 0)
                
                price_raw = h.get('price', {})
                if isinstance(price_raw, dict):
                    price = int(price_raw.get('value', 0) or 0)
                else:
                    price = int(price_raw or 0)
                
                yr_raw = h.get('yearBuilt', {})
                if isinstance(yr_raw, dict):
                    yr = int(yr_raw.get('value', 0) or 0)
                else:
                    yr = int(yr_raw or 0)
                
                sqft_raw = h.get('sqFt', {})
                if isinstance(sqft_raw, dict):
                    sqft = int(sqft_raw.get('value', 0) or 0)
                else:
                    sqft = int(sqft_raw or 0)
                
                addr = f"{h.get('streetLine', '')} {h.get('city', '')} {h.get('state', '')} {h.get('zip', '')}".strip()
                link = h.get('url', '')
                if link and not link.startswith('http'):
                    link = 'https://www.redfin.com' + link
                
                # Check year is reasonable
                if yr > 2030 or yr < 1800:
                    yr = 0
                
                if 2.5 <= baths <= 3.0 and price <= 600000 and price > 0 and yr >= 2017:
                    dup = any(r['address'] == addr for r in results)
                    if not dup:
                        results.append({
                            'address': addr,
                            'price': f"${price:,}",
                            'beds': beds,
                            'baths': baths,
                            'sqft': sqft,
                            'year': yr,
                            'url': link,
                            'source': 'Redfin'
                        })
                        print(f"  MATCH: {addr} | ${price:,} | {beds}bd/{baths}ba | {sqft}sqft | Built:{yr}")
                elif beds >= 5:
                    # Print near-misses for debugging
                    reasons = []
                    if baths < 2.5 or baths > 3.0: reasons.append(f'baths={baths}')
                    if price > 600000: reasons.append(f'price=${price:,}')
                    if yr < 2017 and yr > 0: reasons.append(f'year={yr}')
                    if yr == 0: reasons.append('year=unknown')
                    if reasons:
                        print(f"  NEAR-MISS: {addr} | ${price:,} | {beds}bd/{baths}ba | Built:{yr} | {', '.join(reasons)}")
        else:
            print(f"  {city}: HTTP {resp.status_code}")
    except Exception as e:
        print(f"  Error for {city}: {e}")

print(f"\n\n=== REDFIN TOTAL MATCHING: {len(results)} ===")
for r in results:
    print(f"{r['address']} | {r['price']} | {r['beds']}bd/{r['baths']}ba | {r['sqft']}sqft | Built:{r['year']} | {r['url']}")

with open('all_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to all_results.json")
