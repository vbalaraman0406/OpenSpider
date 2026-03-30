import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'https://www.redfin.com/',
}

# Vancouver WA area zip codes
zips = {
    '98660': 'Vancouver', '98661': 'Vancouver', '98662': 'Vancouver',
    '98663': 'Vancouver', '98664': 'Vancouver', '98665': 'Vancouver',
    '98682': 'Vancouver', '98683': 'Vancouver', '98684': 'Vancouver',
    '98685': 'Vancouver', '98686': 'Vancouver',
    '98604': 'Battle Ground', '98606': 'Brush Prairie',
    '98607': 'Camas/Washougal', '98642': 'Ridgefield',
    '98671': 'Washougal'
}

# First find correct region IDs by looking up each zip
all_homes = []
seen_ids = set()

for zc, area in zips.items():
    try:
        # Look up region ID for this zip
        lookup = f'https://www.redfin.com/stingray/do/location-autocomplete?location={zc}&v=2'
        lr = requests.get(lookup, headers=headers, timeout=10)
        lt = lr.text
        if lt.startswith('{}&&'):
            lt = lt[4:]
        # Parse the autocomplete response to find region ID
        # Format is typically rows with pipe-separated values
        lines = lt.strip().split('\n')
        region_id = None
        region_type = None
        for line in lines:
            parts = line.split('\u0007')
            if len(parts) > 3 and zc in line:
                # Try to extract region info
                for p in parts:
                    if 'region_id' in p or 'id' in p.lower():
                        pass
                # The format has region_id and region_type in specific positions
                # Let me just print the first matching line
                if region_id is None:
                    # Typical format: type\x07id\x07name\x07...
                    try:
                        region_type = int(parts[0]) if parts[0].isdigit() else None
                        region_id = int(parts[1]) if parts[1].isdigit() else None
                    except:
                        pass
        
        if region_id and region_type:
            url = f'https://www.redfin.com/stingray/api/gis?al=1&market=portland&num_homes=350&ord=redfin-recommended-asc&page_number=1&region_id={region_id}&region_type={region_type}&sf=1,2,3,5,6,7&status=9&uipt=1&v=8'
            r = requests.get(url, headers=headers, timeout=15)
            t = r.text
            if t.startswith('{}&&'):
                t = t[4:]
            d = json.loads(t)
            homes = d.get('payload', {}).get('homes', [])
            for h in homes:
                pid = h.get('propertyId', '')
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                price = h.get('price', {}).get('value', 0) if isinstance(h.get('price'), dict) else 0
                beds = h.get('beds', 0)
                baths = h.get('baths', 0)
                yr = h.get('yearBuilt', {}).get('value', 0) if isinstance(h.get('yearBuilt'), dict) else 0
                sqft = h.get('sqFt', {}).get('value', 0) if isinstance(h.get('sqFt'), dict) else 0
                addr = h.get('streetLine', {}).get('value', '') if isinstance(h.get('streetLine'), dict) else h.get('streetLine', '')
                city = h.get('city', '')
                state = h.get('state', '')
                zipcode = h.get('zip', '')
                url_path = h.get('url', '')
                link = f'https://www.redfin.com{url_path}' if url_path else ''
                
                if beds >= 5 and 2.5 <= baths <= 3.0 and price <= 600000 and price > 0 and yr >= 2017:
                    all_homes.append({
                        'price': price, 'addr': addr, 'city': city,
                        'state': state, 'zip': zipcode, 'beds': beds,
                        'baths': baths, 'sqft': sqft, 'year': yr, 'link': link
                    })
            print(f'ZIP {zc} ({area}): region_id={region_id}, type={region_type}, {len(homes)} total, matches so far: {len(all_homes)}')
        else:
            print(f'ZIP {zc} ({area}): Could not find region ID')
    except Exception as e:
        print(f'ZIP {zc} ({area}) error: {e}')

print(f'\n=== TOTAL MATCHING HOMES: {len(all_homes)} ===')
for h in all_homes:
    print(f"${h['price']:,} | {h['addr']}, {h['city']}, {h['state']} {h['zip']} | {h['beds']}bd/{h['baths']}ba | {h['sqft']:,}sqft | Built {h['year']} | {h['link']}")
